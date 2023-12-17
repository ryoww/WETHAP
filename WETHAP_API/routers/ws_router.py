import datetime
import os
import dotenv

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fetchWeather import fetchWeather
from managers import infos_manager, sender_manager, ws_manager

dotenv.load_dotenv()
prefix = f"{os.environ.get('PREFIX')}/ws"
router = APIRouter(prefix=prefix)


def prepare(data):
    if (record := sender_manager.select(uuid=data["uuid"])) is not None:
        record = sender_manager.wrap_records(record)
        return record["labID"]
    else:
        sender_manager.insert(uuid=data["uuid"], labID=data["labID"])
        return data["labID"]


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # NOTE: data = {"uuid": str, "labID": str, (...)}
        data = await websocket.receive_json()
        print(data)
        if not (data.get("uuid") and data.get("labID")):
            print(f"disconnect ({data})")
            await websocket.close(1007)
            ws_manager.disconnect(websocket)
            return
        labID = prepare(data)
        ws_manager.update_info(websocket, data)
        await websocket.send_json({"labID": labID})

        while True:
            data = await websocket.receive_json()
            result = infos_manager.insert(
                labID=data["labID"],
                date=data.get("date", str(datetime.date.today())),
                numGen=data.get("numGen"),
                temperature=data["temperature"],
                humidity=data["humidity"],
                pressure=data["pressure"],
                weather=fetchWeather(),
            )
            print(f"status: {result}, data: {data}")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@router.websocket("/PingPong")
async def ping_pong(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
