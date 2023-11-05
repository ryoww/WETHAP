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
