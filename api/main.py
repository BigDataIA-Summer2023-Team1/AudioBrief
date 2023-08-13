import os
import uvicorn
import tempfile
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request, HTTPException

from models.user import Users, UsersLogin
from utils.rate_limiter import rate_limiter
from utils.gcs_service import read_text_file_without_downloading, read_audio_file_without_downloading
from utils.jwt_validations import validate_jwt_token, fetch_sub_from_token, hash_password, \
    verify_password, create_access_token
from utils.cloud_sql import connect_to_sql, get_sql_client, check_if_user_exist, insert_to_users_table, \
    fetch_authors, fetch_books_by_author, fetch_user_by_email

# load env variables
load_dotenv('../.env')

# FastAPI app
app = FastAPI(title="AudioBrief")


# Routes
@app.get("/api/v1/books/{bookId}/chapters/{chapterId}/summarize")
async def summarize(request: Request, bookId: str, chapterId: str):
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            bearer_token = auth_header.split(' ')[1]
            if validate_jwt_token(bearer_token):
                email, plan = fetch_sub_from_token(bearer_token)
                await rate_limiter(email, plan)

                file_path = f"{bookId}/chapters/{chapterId}/summary.txt"

                summary = read_text_file_without_downloading(file_path)

                return {"summary": summary}
            else:
                raise HTTPException(status_code=401, detail=f"Access denied")
        else:
            raise HTTPException(status_code=401, detail=f"Access token is missing")
    except Exception as e:
        print(str(e))


@app.get("/api/v1/books/{bookId}/chapters/{chapterId}/audio")
async def audio(request: Request, bookId: str, chapterId: str):
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            bearer_token = auth_header.split(' ')[1]
            if validate_jwt_token(bearer_token):
                email, plan = fetch_sub_from_token(bearer_token)
                await rate_limiter(email, plan)

                file_path = f"{bookId}/chapters/{chapterId}/audio.mp3"

                blob = read_audio_file_without_downloading(file_path)
                content_type = blob.content_type or "audio/mp3" or "audio/mpeg"

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                blob.download_to_file(temp_file)

                return StreamingResponse(open(temp_file.name, "rb"), media_type=content_type)
            else:
                raise HTTPException(status_code=401, detail=f"Access denied")
        else:
            raise HTTPException(status_code=401, detail=f"Access token is missing")
    except Exception as e:
        print(str(e))


@app.get("/api/v1/authors")
async def get_authors(request: Request):
    try:
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
    except Exception as e:
        print(str(e))


@app.get("/api/v1/books")
async def get_books(request: Request, author: str = ""):
    try:
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
    except Exception as e:
        print(str(e))


@app.post("/api/v1/users/signup/")
def signup(user: Users):
    try:
        conn = get_sql_client(connect_to_sql)
        user_exists = check_if_user_exist(conn, data={"email": user.email})
        if user_exists:
            raise HTTPException(status_code=400, detail=f"User with email {user.email} already exists!!")

        print(hash_password(user.password))
        insert_to_users_table(conn, [{"email": user.email, "password": hash_password(user.password), "plan": user.plan,
                                      "role": 'user'}])

        return {"email": user.email, "plan": "basic"}
    except Exception as e:
        print(str(e))


@app.post("/api/v1/users/login/")
def login(request: Request, user: UsersLogin):
    try:
        conn = get_sql_client(connect_to_sql)
        user_exists = check_if_user_exist(conn, data={"email": user.email})
        if not user_exists:
            raise HTTPException(status_code=400, detail=f"User with email {user.email} doesn't exists!!")
        user_data = fetch_user_by_email(conn, {"email": user.email})

        if verify_password(user.password, user_data["password"]):
            raise HTTPException(status_code=400, detail=f"user email or password didn't matched.")

        token = create_access_token({"email": user.email, "plan": user_data["plan"], "role": user_data["role"]})

        return {"access_token": token}
    except Exception as e:
        print(str(e))


try:
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = os.getenv("FASTAPI_PORT", 8000)

    uvicorn.run(app, host=host, port=int(port))
except Exception as e:
    print(str(e))
