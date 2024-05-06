from typing import Any

from fastapi import WebSocket


class WebsocketManager:
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


class SenderWebsocketManager(WebsocketManager):
    def __init__(self) -> None:
        super().__init__()
        self.connection_infos: dict[WebSocket, dict[str, Any]] = {}

    @property
    def active_rooms(self):
        return [info["labID"] for info in self.connection_infos.values()]

    async def connect(self, websocket: WebSocket):
        await super().connect(websocket)
        self.connection_infos[websocket] = {}

    def disconnect(self, websocket: WebSocket):
        super().disconnect(websocket)
        del self.connection_infos[websocket]

    def update_info(self, websocket: WebSocket, info: dict):
        self.connection_infos[websocket].update(info)

    async def send_request_info(self, lab_id: str):
        for ws in self.active_connections:
            if self.connection_infos[ws]["labID"] == lab_id:
                await ws.send_json({"message": "request info"})
                print(f"send request to {lab_id}")

    async def send_change_lab_id(self, before, after):
        for ws in self.active_connections:
            if self.connection_infos[ws]["labID"] == before:
                await ws.send_json({"message": "change labID", "new labID": after})
                self.connection_infos[ws]["labID"] = after
                print(f"send change labID {before} to {after}")
