import datetime
import os

import dotenv
import psycopg
from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect
from managers import infos_manager, sender_manager, ws_manager
from utils.fetch_weather import fetch_weather

dotenv.load_dotenv()
prefix = f"{os.environ.get('PREFIX')}/ws"
router = APIRouter(prefix=prefix)


def prepare(data):
    if (record := sender_manager.select(uuid=data["uuid"], wrap=True)) is not None:
        return record["lab_id"]
    elif data["labID"] not in sender_manager.get_all_lab_id():
        try:
            sender_manager.insert(uuid=data["uuid"], lab_id=data["labID"])
        except psycopg.DatabaseError as error:
            print(error)
        return data["labID"]
    else:
        new_id = sender_manager.get_all()[-1]["id"] + 1
        dummy_lab_id = f"dummy{new_id}"
        try:
            sender_manager.insert(uuid=data["uuid"], lab_id=dummy_lab_id)
        except psycopg.DatabaseError as error:
            print(error)
        return dummy_lab_id


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # NOTE: data = {"uuid": str, "labID": str, (...)}
        data = await websocket.receive_json()
        if not (data.get("uuid") and data.get("labID")):
            print(f"disconnect ({data})")
            ws_manager.disconnect(websocket)
            await websocket.close(1007)
            return
        lab_id = prepare(data)
        data["labID"] = lab_id
        ws_manager.update_info(websocket, data)
        print(f"connect {lab_id}")
        await websocket.send_json({"labID": lab_id})

        while True:
            data = await websocket.receive_json()
            if (info := data.get("info")) is not None:
                try:
                    infos_manager.insert(
                        lab_id=info["labID"],
                        date=info.get("date", str(datetime.date.today())),
                        time=info.get("time"),
                        num_gen=info.get("numGen"),
                        temperature=info["temperature"],
                        humidity=info["humidity"],
                        pressure=info["pressure"],
                        weather=fetch_weather(),
                    )
                    result = {"status": "success", "info": {str(info)}}
                    print(result)
                except psycopg.DatabaseError as error:
                    print(error)
                    print({"status": "failed"})

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
