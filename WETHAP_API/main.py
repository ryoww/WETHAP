import asyncio
import datetime
import json
import os

import dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from managers import ws_manager
from routers import http_router, ws_router

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
    datetime.time(10, 7),
    datetime.time(10, 8),
    datetime.time(10, 9),
)

dotenv.load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origin_regex="http://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(http_router.router)
app.include_router(ws_router.router)


def get_numGen():
    now = datetime.datetime.now().time().replace(second=0, microsecond=0)
    return FINISH_TIMES.index(now) + 1


async def request_info(numGen=None):
    numGen = get_numGen()
    massage = {"massage": "request info", "numGen": numGen}
    print(massage)
    await ws_manager.broadcast(json.dumps(massage))


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
    uvicorn_config = uvicorn.Config(app, port=int(os.environ.get("SERVER_PORT")))
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
