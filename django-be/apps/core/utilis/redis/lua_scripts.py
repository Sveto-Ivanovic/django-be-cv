lua_token_request_limiter = """
local key = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call('HGETALL', key)
local tokens = max_tokens
local last_refill = now

if #data > 0 then
  local fields = {}
  for i = 1, #data, 2 do
    fields[data[i]] = data[i + 1]
  end
  tokens = tonumber(fields['tokens']) or max_tokens
  last_refill = tonumber(fields['last_refill']) or now
end

-- Refill tokens based on elapsed time
local elapsed = now - last_refill
local new_tokens = elapsed * refill_rate
tokens = math.min(max_tokens, tokens + new_tokens)

local allowed = 0
local remaining = tokens

if tokens >= 1 then
  tokens = tokens - 1
  remaining = tokens
  allowed = 1
end

redis.call('HSET', key, 'tokens', tostring(tokens), 'last_refill', tostring(now))
redis.call('EXPIRE', key, math.ceil(max_tokens / refill_rate) + 1)

return { allowed, math.floor(remaining) }
"""

lua_task_blocker = """
local key = KEYS[1]
local max_limit = tonumber(ARGV[1])
local exp = tonumber(ARGV[2])
local mode = ARGV[3]

local current = tonumber(redis.call('HGET', key, 'num_of_tasks') or '0')

if mode == 'start' then
    if current < max_limit then
        current = current + 1
        redis.call('HSET', key, 'num_of_tasks', current)
        redis.call('EXPIRE', key, exp)
        return 1
    end
    return 0
else
    current = math.max(current - 1, 0)
    redis.call('HSET', key, 'num_of_tasks', current)
    redis.call('EXPIRE', key, exp)
    if current < max_limit then return 1 else return 0 end
end
"""