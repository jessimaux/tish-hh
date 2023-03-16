from fastapi import APIRouter, WebSocket, Security, WebSocketDisconnect, \
    status, HTTPException

from apps.users.schemas import UserRetrieve
from apps.auth.dependencies import get_current_active_user
from .connection import ConnectionManager
from .crud import *


router = APIRouter()
manager = ConnectionManager()


@router.get('/messages/get_messages/', tags=['messages'])
async def get_messages_for_room(user_id: int = 0,
                                offset: int = 0,
                                size: int = 50,
                                current_user: UserRetrieve = Security(get_current_active_user, scopes=['messages'])):
    messages = await get_messages(current_user.id, user_id, offset, size)
    return messages


@router.get('/messages/get_rooms/', tags=['messages'])
async def get_rooms_for_user(current_user: UserRetrieve = Security(get_current_active_user, scopes=['messages'])):
    rooms = await get_rooms(current_user.id)
    return rooms


@router.websocket('/messages/')
async def websocket_endpoint(websocket: WebSocket = WebSocket,
                             current_user: UserRetrieve = Security(get_current_active_user, scopes=['messages'])):
    await manager.connect(current_user.id, websocket)

    try:
        while True:
            # receive websocket message, add it to redis stream and chat room
            data = await websocket.receive_text()
            data_dict = json.loads(data)
            await add_to_stream('messages', data_dict)
            await add_to_room(current_user.id, data_dict['user_id'], data)
            await add_room(current_user.id, data_dict['user_id'])

            # read from redis stream, if there are messages, send it to users
            response = await get_from_stream(stream_channel='messages')
            for stream, messages in response:
                for message in messages:
                    message_id, message_text = message
                    # maybe need to decode
                    # message_text_decode = {y.decode('utf8'): message_text.get(y).decode('utf8') for y in message_text.keys()}
                    await manager.send_personal_message(str(message_text), int(message_text[b'user_id']))
                    await del_from_stream('messages', message_id)

    except WebSocketDisconnect:
        manager.disconnect(current_user.id, websocket)
