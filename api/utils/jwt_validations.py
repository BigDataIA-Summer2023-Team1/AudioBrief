import os
import jwt
import bcrypt
import time
import datetime


def create_access_token(data: dict):
    try:
        payload = {
            **data,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]))
        }

        token = jwt.encode(payload, os.environ["SECRET_KEY"], os.environ["ALGORITHM"])

        return token
    except Exception as e:
        print(str(e))


def hash_password(password):
    try:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode("utf-8")
    except Exception as e:
        print(str(e))


def verify_password(plain_password, hashed_password):
    try:
        salt = bcrypt.gensalt()
        return bcrypt.checkpw(bcrypt.hashpw(plain_password.encode('utf-8'), salt), hashed_password.encode('utf-8'))
    except Exception as e:
        print(str(e))


def fetch_sub_from_token(jwt_token):
    try:
        decoded_token = jwt.decode(jwt_token, os.environ["SECRET_KEY"], algorithms=os.environ["ALGORITHM"])
        email = decoded_token.get("email")
        plan = decoded_token.get("plan")

        return email, plan
    except Exception as e:
        print(str(e))


def compare_time(token_time: int):
    try:
        if int(time.time()) < token_time:
            return True
        else:
            return False
    except Exception as e:
        print(str(e))


def validate_jwt_token(generated_token):
    try:
        secret_key = os.getenv("SECRET_KEY")
        algorithm = os.getenv("ALGORITHM")

        try:
            decoded_token = jwt.decode(generated_token, secret_key, algorithms=[algorithm])
            return compare_time(decoded_token['exp'])

        except jwt.ExpiredSignatureError:
            return False
        except Exception as e:
            return False
    except Exception as e:
        print(str(e))
