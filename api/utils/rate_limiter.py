import os
import redis
import datetime
# from cloud_logger import logger
from fastapi import HTTPException
from google.cloud import logging as gcl


def get_redis_pool():
    try:
        REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        REDIS_PORT = os.getenv("REDIS_PORT", 6379)

        return redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True)
    except Exception as exp:
        print(str(exp))


# Rate limiter dependency
async def rate_limiter(user_id: str, plan: str):
    # log = logger()
    # resource = gcl.Resource(type='global', labels={"type": "application"})
    try:
        client = get_redis_pool()

        current_count = client.get(user_id)
        if current_count is None:
            client.setex(user_id, 86400, 1)  # Set the count to 1 and expire after 24 hours
        elif plan == "basic" and int(current_count) >= 100:
            # payload = {
            #     "endpoint": "",
            #     "timestamp": datetime.datetime.now(),
            #     "user": user_id,
            #     "status": 429,
            #     "execution_time": "",
            #     "msg": "Request limit exceeded for a basic plan"
            # }
            #
            # log.log_text(str(payload), resource=resource, severity="ERROR")
            raise HTTPException(status_code=429, detail="Request limit exceeded")
        elif plan == "premium" and int(current_count) >= 20:
            # payload = {
            #     "endpoint": "",
            #     "timestamp": datetime.datetime.now(),
            #     "user": user_id,
            #     "status": 429,
            #     "execution_time": "",
            #     "msg": "Request limit exceeded for a premium plan"
            # }
            #
            # log.log_text(str(payload), resource=resource, severity="ERROR")
            raise HTTPException(status_code=429, detail="Request limit exceeded")
        else:
            client.incr(user_id)
    except Exception as exp:
        # payload = {
        #     "endpoint": "",
        #     "timestamp": datetime.datetime.now(),
        #     "user": user_id,
        #     "status": 429,
        #     "execution_time": "",
        #     "msg": str(exp)
        # }
        #
        # log.log_text(str(payload), resource=resource, severity="ERROR")
        print(str(exp))

