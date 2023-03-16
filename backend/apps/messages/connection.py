from fastapi import WebSocket
        

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = dict()

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if self.active_connections.get(user_id):
            self.active_connections[user_id].append(websocket)
        else:
            self.active_connections[user_id] = [websocket]

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: str, user_id: int):
        websocket_list = self.active_connections.get(user_id)
        if websocket_list:
            for websocket in websocket_list:
                await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for websocket_list in self.active_connections.values():
            if websocket_list:
                for websocket in websocket_list:
                    await websocket.send_text(message)
            