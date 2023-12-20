import os

import dotenv
from fastapi import APIRouter, Response, status
from fetchWeather import fetchWeather
from managers import infos_manager, ws_manager

from routers.router_depends import Info, requestInfo

dotenv.load_dotenv()
prefix = os.environ.get("PREFIX")
router = APIRouter(prefix=prefix)


@router.get("/")
async def index():
    return {"status": "online"}


@router.post("/addInfo", status_code=status.HTTP_200_OK)
async def add_info(info: Info, response: Response):
    print(f"addInfo request: {info}")
    if infos_manager.insert(
        lab_id=info.labID,
        date=info.date,
        num_gen=info.numGen,
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
    response = infos_manager.select(lab_id=labID, date=date, num_gen=numGen)
    return response if response else "NoData"


@router.get("/activeRooms")
async def active_rooms():
    print(ws_manager.connection_infos)
    response = [
        info["lab_id"]
        for info in ws_manager.connection_infos.values()
        if info.get("lab_id")
    ]
    return response if response else "NoActiveRooms"


@router.post("/requestInfo", status_code=status.HTTP_200_OK)
async def request_info(request: requestInfo, response: Response):
    print(f"receive request {request.labID}")
    if request.labID in ws_manager.active_rooms:
        await ws_manager.send_request_info(request.labID)
        return {"status": "request sended"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "non active room"}
