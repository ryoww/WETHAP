import asyncio
import datetime
import json
import os

import dotenv
import uvicorn
from DB_manager import infosManager
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fetchWeather import fetchWeather
from pydantic import BaseModel
from ws_manager import websocketManager


class Info(BaseModel):
    labID: str
    date: str | datetime.date = str(datetime.date.today())
    numGen: int
    temperature: float
    humidity: float
    pressure: float


FINISH_TIME = (
    datetime.time(9, 25),
    datetime.time(10, 10),
    datetime.time(11, 10),
    datetime.time(11, 55),
    datetime.time(13, 30),
    datetime.time(14, 15),
    datetime.time(15, 15),
    datetime.time(16, 00),
    datetime.time(17, 00),
    datetime.time(17, 45),
    datetime.time(18, 45),
    datetime.time(19, 30),
)

dotenv.load_dotenv()
db_config = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
}
prefix = os.environ.get("PREFIX")

app = FastAPI()

ws_manager = websocketManager()
db_manager = infosManager(table="infos", **db_config)

loop = asyncio.get_event_loop()


def insert_data(data):
    json_data = json.loads(data)
    db_manager.insert(
        labID=json_data["labID"],
        date=json_data.get("date", str(datetime.date.today())),
        numGen=json_data["numGen"],
        temperature=json_data["temperature"],
        humidity=json_data["humidity"],
        pressure=json_data["pressure"],
        weather=fetchWeather(),
    )
    print(json_data)


@app.websocket(f"{prefix}/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            insert_data(data)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get(f"{prefix}/")
async def index():
    return {"status": "online"}


@app.post(f"{prefix}/addInfo/")
async def add_info(data: Info):
    db_manager.insert(
        labID=data.labID,
        # date=str(datetime.date.today()),
        date=data.date,
        numGen=data.numGen,
        temperature=data.temperature,
        humidity=data.humidity,
        pressure=data.pressure,
        weather=fetchWeather(),
    )
    print(data)
    return {"status": "added"}


@app.get(f"{prefix}/isRegistered/")
async def is_registered(labID: str):
    response = db_manager.is_registered(labID)
    return str(response)


@app.get(f"{prefix}/registeredRooms/")
async def registered_rooms():
    response = db_manager.registered_rooms()
    return response


@app.get(f"{prefix}/previewData/")
async def preview_data():
    response = db_manager.preview_data()
    return response


@app.get(f"{prefix}/getInfo/")
async def get_info(labID: str, date: str, numGen: int):
    response = db_manager.select(labID=labID, date=date, numGen=numGen)
    return response if response else "NoData"


async def request_info():
    print("request info")
    await ws_manager.broadcast("request info")


async def run_at(schedule_times: list[datetime.time]):
    loop = asyncio.get_event_loop()
    while True:
        now = datetime.datetime.now()
        next_run_time: datetime.datetime = None

        for schedule_time in schedule_times:
            schedule_datetime = now.replace(
                hour=schedule_time.hour,
                minute=schedule_time.minute,
                second=0,
                microsecond=0,
            )
            if schedule_datetime < now:
                schedule_datetime += datetime.timedelta(days=1)
            if next_run_time is None or schedule_datetime < next_run_time:
                next_run_time = schedule_datetime
        time_until_next_run = (next_run_time - now).total_seconds()
        await asyncio.sleep(time_until_next_run)
        loop.create_task(request_info())


async def start_app():
    uvicorn_config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    loop.create_task(run_at(FINISH_TIME))
    loop.create_task(start_app())
    loop.run_forever()
