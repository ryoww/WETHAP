import os

import dotenv
from fastapi import APIRouter, Response, status
from fetchWeather import fetchWeather
from managers import infos_manager, sender_manager, ws_manager

from routers.router_depends import Info, RequestChange, RequestInfo

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
async def get_a_info(labID: str, date: str, numGen: int):
    response = infos_manager.select(lab_id=labID, date=date, num_gen=numGen)
    return response if response else "NoData"


# ここから新API仕様
@router.get("/infos")
async def get_infos(raw: bool = False):
    if raw:
        response = infos_manager.get_all()
    else:
        response = infos_manager.preview_data()
    return response


@router.get("/info")
async def get_info(labID: str, date: str, numGen: int):
    response = infos_manager.select(lab_id=labID, date=date, num_gen=numGen)
    return response if response else "NoData"


@router.post("/info", status_code=status.HTTP_200_OK)
async def post_info(info: Info, response: Response):
    print(f"post info request: {info}")
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


@router.get("/is-registered")
async def get_is_registered(labID: str):
    response = infos_manager.is_registered(labID)
    return "true" if response else "false"


@router.get("/lab-ids")
async def get_lab_ids():
    response = infos_manager.registered_rooms()
    return response


@router.patch("/lab-ids", status_code=status.HTTP_200_OK)
async def patch_lab_ids(request: RequestChange, response: Response):
    print(request)
    if request.id is None != request.before_labID is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "You must specify either the 'id' or 'before_labID'; both cannot be omitted."
    elif request.after_labID is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "after_labID is required."
    elif request.after_labID in sender_manager.get_all_lab_id():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "after_labID already exists."
    if sender_manager.change_lab_id(
        after_lab_id=request.after_labID,
        id=request.id,
        before_lab_id=request.before_labID,
    ):
        before = (
            sender_manager.get_lab_id(request.id)
            if request.before_labID is None
            else request.before_labID
        )
        await ws_manager.send_change_lab_id(before, request.after_labID)
        return "labID changed."
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "before_labID is an non-existent labID."


@router.get("/active-rooms")
async def get_active_rooms():
    print(ws_manager.connection_infos)
    response = [
        info["labID"]
        for info in ws_manager.connection_infos.values()
        if info.get("labID")
    ]
    return response if response else "NoActiveRooms"


@router.post("/request", status_code=status.HTTP_200_OK)
async def post_request_info(request: RequestInfo, response: Response):
    print(f"receive request {request.labID}")
    if request.labID in ws_manager.active_rooms:
        await ws_manager.send_request_info(request.labID)
        return {"status": "request sended"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "non active room"}
