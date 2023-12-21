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
    if (record := sender_manager.select(uuid=data["uuid"], wrap=True)) is not None:
        return record["lab_id"]
    elif data["labID"] not in sender_manager.get_all_lab_id():
        sender_manager.insert(uuid=data["uuid"], lab_id=data["labID"])
        return data["labID"]
    else:
        new_id = sender_manager.get_all()[-1]["id"] + 1
        dummy_lab_id = f"dummy{new_id}"
        sender_manager.insert(uuid=data["uuid"], lab_id=dummy_lab_id)
        return dummy_lab_id


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # NOTE: data = {"uuid": str, "labID": str, (...)}
        data = await websocket.receive_json()
        if not (data.get("uuid") and data.get("labID")):
            print(f"disconnect ({data})")
            await websocket.close(1007)
            ws_manager.disconnect(websocket)
            return
        lab_id = prepare(data)
        data["labID"] = lab_id
        ws_manager.update_info(websocket, data)
        print(f"connect {lab_id}")
        await websocket.send_json({"labID": lab_id})

        while True:
            data = await websocket.receive_json()
            result = infos_manager.insert(
                lab_id=data["labID"],
                date=data.get("date", str(datetime.date.today())),
                num_gen=data.get("numGen"),
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
