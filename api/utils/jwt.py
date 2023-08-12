import os
import re
import time
import redis
from jose import jwt
# from dotenv import load_dotenv
from datetime import datetime, timedelta
import bcrypt

# load env variables
# load_dotenv('./.env')


def is_valid_email(email):
    pattern = r'^\w+@gmail\.com$'
    return re.match(pattern, email) is not None


def is_valid_password(password):
    # Minimum length: 5 characters
    # At least one uppercase letter
    # At least one lowercase letter
    pattern = r'^(?=.*[A-Z])(?=.*[a-z]).{5,}$'
    return re.match(pattern, password) is not None


def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    return hashed_password.decode()


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode('utf-8'))


def create_access_token(data: dict):
    secret_key = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM")
    expiry_time = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=float(expiry_time))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt


def compare_time(token_time: int):
    if int(time.time()) < token_time:
        return True
    else:
        return False


def validate_jwt_token(generated_token):
    secret_key = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM")

    try:
        decoded_token = jwt.decode(generated_token, secret_key, algorithms=[algorithm])
        return compare_time(decoded_token['exp'])

    except jwt.ExpiredSignatureError:
        # Handle expired token error
        return False
    except Exception as e:
        return False



def redis_conn(db_host, db_port, db_username="", db_password="", decode_responses=True):
    # TODO: validation & try except
    return redis.Redis(host=db_host, port=db_port, username=db_username, password= db_password, decode_responses = decode_responses)
