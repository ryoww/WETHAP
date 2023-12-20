from typing import Any

from fastapi import WebSocket


class websocketManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: Any):
        print(type(message), message)
        if isinstance(message, str):
            await websocket.send_text(message)
        elif isinstance(message, dict):
            await websocket.send_json(message)
        else:
            await websocket.send_bytes(message)

    async def broadcast(self, message: Any, websocket: WebSocket = None):
        connections = self.active_connections
        if websocket is not None:
            connections = [
                connection for connection in connections if connection != websocket
            ]
        for connection in connections:
            await self.send_message(connection, message)


class senderWebsocketManager(websocketManager):
    def __init__(self) -> None:
        super().__init__()
        self.connection_infos: dict[WebSocket, dict[str, Any]] = {}
        self.active_rooms: list[str] = []

    async def connect(self, websocket: WebSocket):
        await super().connect(websocket)
        self.connection_infos[websocket] = {}

    def disconnect(self, websocket: WebSocket):
        super().disconnect(websocket)
        if (lab_id := self.connection_infos[websocket].get("lab_id")) is not None:
            self.active_rooms.remove(lab_id)
        del self.connection_infos[websocket]

    def update_info(self, websocket: WebSocket, info: dict):
        self.connection_infos[websocket].update(info)
        if (lab_id := info.get("lab_id")) is not None:
            self.active_rooms.append(lab_id)

    async def send_request_info(self, lab_id: str):
        for ws in self.active_connections:
            if self.connection_infos[ws]["lab_id"] == lab_id:
                await ws.send_json({"message": "request info"})
                print(f"send request to {lab_id}")
