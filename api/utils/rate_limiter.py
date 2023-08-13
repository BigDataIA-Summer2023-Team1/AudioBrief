import os
import redis
from fastapi import HTTPException


def get_redis_pool():
    try:
        REDIS_HOST = os.environ["REDIS_HOST"]
        REDIS_PORT = os.environ["REDIS_PORT"]

        return redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True)
    except Exception as exp:
        print(str(exp))


# Rate limiter dependency
async def rate_limiter(user_id: str, plan: str):
    try:
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
    except Exception as exp:
        print(str(exp))

