import json
import datetime

import redis.asyncio as redis

import settings
from .utils import get_room_id


# TODO: maybe rewrite as dependency with context manager ?
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


async def get_messages(user_id_1, user_id_2: int, offset: int = 0, size: int = 50):
    """Check if room with id exists; fetch messages limited by size"""
    room_key = f'room:{get_room_id(user_id_1, user_id_2)}'
    room_exists = await redis_client.exists(room_key)
    if not room_exists:
        return []
    else:
        values = await redis_client.zrevrange(room_key, offset, offset + size)
        return list(map(lambda x: json.loads(x.decode("utf-8")), values))
    
    
async def get_rooms(user_id: int):
    """Get all user's rooms"""
    user_key = f'user:{user_id}:rooms'
    user_exists = await redis_client.exists(user_key)
    if not user_exists:
        return []
    else:
        values = await redis_client.smembers(user_key)
        return list(map(lambda x: json.loads(x.decode("utf-8")), values))
    

async def add_to_stream(stream_channel:str, data: dict):
    msg_id = await redis_client.xadd(stream_channel, data, '*')
    return msg_id


async def get_from_stream(stream_channel: str, count: int | None = None, block:int | None = None):
    response = await redis_client.xread({stream_channel: '0-0'}, count, block)
    return response


async def del_from_stream(stream_channel: any, message_id: any):
    await redis_client.xdel(stream_channel, message_id)


async def add_to_room(user_id_1: int, user_id_2: int, message: str):
    room_key = f'room:{get_room_id(user_id_1, user_id_2)}'
    await redis_client.zadd(room_key, {message: int(round(datetime.datetime.now().timestamp()))})

async def add_room(user_id: int, user_id_add: int):
    user_rooms_key = f'user:{user_id}:rooms'
    await redis_client.sadd(user_rooms_key, user_id_add)