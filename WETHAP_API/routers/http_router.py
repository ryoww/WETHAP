import os

import dotenv
from fastapi import APIRouter, Response, status
from fetchWeather import fetchWeather
from managers import infos_manager, ws_manager

from routers.router_depends import Info

dotenv.load_dotenv()
prefix = os.environ.get("PREFIX")
router = APIRouter(prefix=prefix)


@router.get("/")
async def index():
    return {"status": "online"}


@router.post("/addInfo", status_code=status.HTTP_200_OK)
async def add_info(info: Info, response: Response):
    print(info)
    if infos_manager.insert(
        labID=info.labID,
        date=info.date,
        numGen=info.numGen,
        temperature=info.temperature,
        humidity=info.humidity,
        pressure=info.pressure,
        weather=fetchWeather(),
    ):
        return {"status": "added"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "failed"}


@router.get("/isRegistered")
async def is_registered(labID: str):
    response = infos_manager.is_registered(labID)
    return str(response)


@router.get("/registeredRooms")
async def registered_rooms():
    response = infos_manager.registered_rooms()
    return response


@router.get("/previewData")
async def preview_data():
    response = infos_manager.preview_data()
    return response


@router.get("/previewRawData")
async def preview_raw_data():
    response = infos_manager.get_all()
    return response


@router.get("/getInfo")
async def get_info(labID: str, date: str, numGen: int):
    response = infos_manager.select(labID=labID, date=date, numGen=numGen)
    return response if response else "NoData"


@router.get("/activeRooms")
async def active_rooms():
    print(ws_manager.connection_infos)
    response = [
        info["labID"]
        for info in ws_manager.connection_infos.values()
        if info.get("labID")
    ]
    return response if response else "NoActiveRooms"


@router.post("/requestInfo", status_code=status.HTTP_200_OK)
async def request_info(labID: str, response: Response):
    print(f"receive request {labID}")
    if labID in ws_manager.active_rooms:
        await ws_manager.send_request_info(labID)
        return {"status": "request sended"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "non active room"}
