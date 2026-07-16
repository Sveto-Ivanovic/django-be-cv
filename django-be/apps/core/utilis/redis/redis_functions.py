import time
from typing import Literal
import redis
from dotenv import load_dotenv
import os
from .lua_scripts import lua_task_blocker, lua_token_request_limiter

load_dotenv()


r = redis.Redis(host=os.getenv("REDIS_HOST"),port=6379,decode_responses=True)

enableTask = r.register_script(lua_task_blocker)
rateLimiter = r.register_script(lua_token_request_limiter)

def canTask(user_id: str, task_name: str, max_limit: int, exp: int, mode: Literal['start', 'finish']):
    task_id = f"user:{user_id}:task:{task_name}"
    response = enableTask(keys=[task_id], args=[max_limit, exp, mode])
    return bool(response)
    

def canRequest(user_id: str, action_name: str, max_tokens: float, refill_rate: float) -> tuple[bool, int]:
    key = f"user:{user_id}:ratelimit:{action_name}"
    now = time.time()
    allowed, remaining = rateLimiter(keys=[key], args=[max_tokens, refill_rate, now])
    return bool(allowed), int(remaining)