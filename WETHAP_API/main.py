import asyncio
import datetime
import os

import dotenv
import psycopg2
import uvicorn
from DB_manager import infosManager, senderManager
from fastapi import FastAPI, status, Response
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fetchWeather import fetchWeather
from pydantic import BaseModel
from utils.ws_manager import websocketManager


class Info(BaseModel):
    labID: str
    date: str | datetime.date = str(datetime.date.today())
    numGen: int
    temperature: float
    humidity: float
    pressure: float


FINISH_TIMES = (
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
prefix = os.environ.get("PREFIX")
db_config = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
}

app = FastAPI()
ws_manager = websocketManager()
db_manager = infosManager(table="infos", **db_config)
sender_db_manager = senderManager(table="senders", **db_config)


def insert_data(data):
    data
    db_manager.insert(
        labID=data["labID"],
        date=data.get("date", str(datetime.date.today())),
        numGen=data["numGen"],
        temperature=data["temperature"],
        humidity=data["humidity"],
        pressure=data["pressure"],
        weather=fetchWeather(),
    )
    print(data)


def prepare(data):
    if (record := sender_db_manager.select(uuid=data["uuid"])) is not None:
        record = sender_db_manager.wrap_records(record)
        return record["labID"]
    else:
        sender_db_manager.insert(uuid=data["uuid"], labID=data["labID"])
        return data["labID"]


@app.websocket(f"{prefix}/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # data = {"uuid": str, "labID": str, (...)}
        data = await websocket.receive_json()
        labID = prepare(data)
        await websocket.send_json({"labID": labID})

        while True:
            data = await websocket.receive_json()
            insert_data(data)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get(f"{prefix}/")
async def index():
    return {"status": "online"}


@app.post(f"{prefix}/addInfo/", status_code=status.HTTP_200_OK)
async def add_info(data: Info, response: Response):
    # try:
    if db_manager.insert(
        labID=data.labID,
        # date=str(datetime.date.today()),
        date=data.date,
        numGen=data.numGen,
        temperature=data.temperature,
        humidity=data.humidity,
        pressure=data.pressure,
        weather=fetchWeather(),
    ):
        print(data)
        return {"status": "added"}
    else:
        print(data)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "failed"}


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
        await request_info()


async def start_app():
    uvicorn_config = uvicorn.Config(
        app, host="0.0.0.0", port=int(os.environ.get("SERVER_PORT"))
    )
    server = uvicorn.Server(uvicorn_config)
    try:
        await server.serve()
    finally:
        [task.cancel() for task in asyncio.all_tasks()]


async def main():
    tasks = [run_at(FINISH_TIMES), start_app()]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("server killed")


if __name__ == "__main__":
    asyncio.run(main())
