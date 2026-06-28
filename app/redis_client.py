import redis.asyncio as aioredis
from app.config import REDIS_URL


# We need to maintain two clients here - async and sync
# async for the fastAPI router handlers 
# sync for the subscriber threads

redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
