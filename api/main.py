import os
import jwt
import bcrypt
import uvicorn
import time
from dotenv import load_dotenv

from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request, HTTPException, Depends
import redis
import datetime
from utils.cloud_sql import connect_to_sql, get_sql_client, check_if_user_exist, insert_to_users_table, \
    fetch_authors, fetch_books_by_author, fetch_user_by_email
from utils.gcs_service import read_text_file_without_downloading, read_audio_file_without_downloading

# load env variables
load_dotenv('../.env')

# FastAPI app
app = FastAPI(title="AudioBrief")


class Users(BaseModel):
    email: str
    password: str
    plan: str


class UsersLogin(BaseModel):
    email: str
    password: str


# Generate JWT token
def create_access_token(data: dict):
    payload = {
        **data,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    }

    token = jwt.encode(payload, os.environ["SECRET_KEY"], os.environ["ALGORITHM"])

    return token


def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode("utf-8")


def verify_password(plain_password, hashed_password):
    salt = bcrypt.gensalt()
    return bcrypt.checkpw(bcrypt.hashpw(plain_password.encode('utf-8'), salt), hashed_password.encode('utf-8'))


def fetch_sub_from_token(jwt_token):
    decoded_token = jwt.decode(jwt_token, os.environ["SECRET_KEY"], algorithms=os.environ["ALGORITHM"])
    email = decoded_token.get("email")
    plan = decoded_token.get("plan")

    return email, plan


def compare_time(token_time: int):
    if int(time.time()) < token_time:
        return True
    else:
        return False


def validate_jwt_token(generated_token):
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")

    try:
        decoded_token = jwt.decode(generated_token, secret_key, algorithms=[algorithm])
        return compare_time(decoded_token['exp'])

    except jwt.ExpiredSignatureError:
        return False
    except Exception as e:
        return False


def get_redis_pool():
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = os.environ["REDIS_PORT"]

    return redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True)


# Rate limiter dependency
async def rate_limiter(user_id: str, plan: str):
    client = get_redis_pool()

    current_count = client.get(user_id)
    if current_count is None:
        client.setex(user_id, 86400, 1)  # Set the count to 1 and expire after 24 hours
    elif plan == "basic" and int(current_count) >= 10:
        raise HTTPException(status_code=429, detail="Request limit exceeded")
    elif plan == "premium" and int(current_count) >= 20:
        raise HTTPException(status_code=429, detail="Request limit exceeded")
    else:
        client.incr(user_id)


# Routes
@app.get("/api/v1/books/{bookId}/chapters/{chapterId}/summarize")
async def summarize(request: Request, bookId: str, chapterId: str):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        bearer_token = auth_header.split(' ')[1]
        if validate_jwt_token(bearer_token):
            email, plan = fetch_sub_from_token(bearer_token)
            await rate_limiter(email, plan)

            file_path = f"{bookId}/chapters/{chapterId}/summary.txt"

            # summary = read_text_file_without_downloading(file_path)

            return {"summary": "HI"}
        else:
            raise HTTPException(status_code=401, detail=f"Access denied")
    else:
        raise HTTPException(status_code=401, detail=f"Access token is missing")


@app.get("/api/v1/books/{bookId}/chapters/{chapterId}/audio")
async def audio(request: Request, bookId: str, chapterId: str):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        bearer_token = auth_header.split(' ')[1]
        if validate_jwt_token(bearer_token):
            email, plan = fetch_sub_from_token(bearer_token)
            await rate_limiter(email, plan)

            file_path = f"{bookId}/chapters/{chapterId}/audio.mp3"

            blob = read_audio_file_without_downloading(file_path)
            content_type = blob.content_type or "application/pdf"
            downloaded_data = blob.download_as_bytes()

            return StreamingResponse(iter(downloaded_data), media_type=content_type)
        else:
            raise HTTPException(status_code=401, detail=f"Access denied")
    else:
        raise HTTPException(status_code=401, detail=f"Access token is missing")


@app.get("/api/v1/authors")
async def get_authors(request: Request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        bearer_token = auth_header.split(' ')[1]
        if validate_jwt_token(bearer_token):
            conn = get_sql_client(connect_to_sql)
            authors = fetch_authors(conn)
            authors = [author[0] for author in authors]

            return authors
        else:
            raise HTTPException(status_code=401, detail=f"Access denied")
    else:
        raise HTTPException(status_code=401, detail=f"Access token is missing")


@app.get("/api/v1/books")
async def get_books(request: Request, author: str = ""):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        bearer_token = auth_header.split(' ')[1]
        if validate_jwt_token(bearer_token):
            conn = get_sql_client(connect_to_sql)
            data = {}

            if author != "":
                data = {"author": author}

            books = fetch_books_by_author(conn, data)

            return books
        else:
            raise HTTPException(status_code=401, detail=f"Access denied")
    else:
        raise HTTPException(status_code=401, detail=f"Access token is missing")


@app.post("/api/v1/users/signup/")
def signup(user: Users):
    conn = get_sql_client(connect_to_sql)
    user_exists = check_if_user_exist(conn, data={"email": user.email})
    if user_exists:
        raise HTTPException(status_code=400, detail=f"User with email {user.email} already exists!!")

    print(hash_password(user.password))
    insert_to_users_table(conn, [{"email": user.email, "password": hash_password(user.password), "plan": user.plan,
                                  "role": 'user'}])

    return {"email": user.email, "plan": "basic"}


@app.post("/api/v1/users/login/")
def login(request: Request, user: UsersLogin):
    conn = get_sql_client(connect_to_sql)
    user_exists = check_if_user_exist(conn, data={"email": user.email})
    if not user_exists:
        raise HTTPException(status_code=400, detail=f"User with email {user.email} doesn't exists!!")
    user_data = fetch_user_by_email(conn, {"email": user.email})

    if verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=400, detail=f"user email or password didn't matched.")

    token = create_access_token({"email": user.email, "plan": user_data["plan"], "role": user_data["role"]})

    return {"access_token": token}


host = os.getenv("FASTAPI_HOST", "localhost")
port = os.getenv("FASTAPI_PORT", 8000)

uvicorn.run(app, host=host, port=int(port))
