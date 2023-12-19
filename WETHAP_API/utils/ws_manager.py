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
        super().connect(websocket)
        self.connection_infos[websocket] = {}

    def disconnect(self, websocket: WebSocket):
        super().disconnect(websocket)
        if (labID := self.connection_infos[websocket].get("labID")) is not None:
            self.active_rooms.remove(labID)
        del self.connection_infos[websocket]

    def update_info(self, websocket: WebSocket, info: dict):
        self.connection_infos[websocket].update(info)
        if (labID := info.get("labID")) is not None:
            self.active_rooms.append(labID)

    async def send_request_info(self, labID: str):
        for ws in self.active_connections:
            if self.connection_infos[ws]["labID"] == labID:
                await ws.send_json({"massage": "request info"})

                print("send request")
