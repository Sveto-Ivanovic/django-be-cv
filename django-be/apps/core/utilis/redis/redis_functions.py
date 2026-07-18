import time
from typing import Literal
import redis
from dotenv import load_dotenv
import os
from .lua_scripts import lua_task_blocker, lua_token_request_limiter

load_dotenv()


r = redis.Redis(host=os.getenv("REDIS_HOST"),port=6379,decode_responses=True, password=os.getenv("REDIS_PASSWORD"))

enableTask = r.register_script(lua_task_blocker)
rateLimiter = r.register_script(lua_token_request_limiter)

def get_client_ip(request):
    xreal_ip = request.META.get('HTTP_X_REAL_IP')
    if xreal_ip:
        return xreal_ip.strip()
    
    xforwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if xforwarded_for:
        return xforwarded_for.split(',')[0].strip()

    return request.META.get('REMOTE_ADDR')


def canTask(user_id: str, task_name: str, max_limit: int, exp: int, mode: Literal['start', 'finish']):
    task_id = f"user:{user_id}:task:{task_name}"
    response = enableTask(keys=[task_id], args=[max_limit, exp, mode])
    return bool(response)
    

def canRequest(user_id: str, action_name: str, max_tokens: float, refill_rate: float) -> tuple[bool, int]:
    key = f"user:{user_id}:ratelimit:{action_name}"
    now = time.time()
    allowed, remaining = rateLimiter(keys=[key], args=[max_tokens, refill_rate, now])
    return bool(allowed), int(remaining)