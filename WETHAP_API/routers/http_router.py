import os

import dotenv
from fastapi import APIRouter, Response, status
from managers import infos_manager, sender_manager, ws_manager
from utils.fetch_weather import fetch_weather
import psycopg
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
    info = {
        "lab_id": info.labID,
        "date": info.date,
        "time": info.time,
        "num_gen": info.numGen,
        "temperature": info.temperature,
        "humidity": info.humidity,
        "pressure": info.pressure,
        "weather": fetch_weather(),
    }
    try:
        infos_manager.insert(**info)
        return {"status": "added", "info": info}
    except psycopg.DatabaseError as error:
        print(error)
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
    info = {
        "lab_id": info.labID,
        "date": info.date,
        "time": info.time,
        "num_gen": info.numGen,
        "temperature": info.temperature,
        "humidity": info.humidity,
        "pressure": info.pressure,
        "weather": fetch_weather(),
    }
    try:
        infos_manager.insert(**info)
        return {"status": "added", "info": info}
    except psycopg.DatabaseError as error:
        print(error)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "failed"}


@router.delete("/info", status_code=status.HTTP_200_OK)
async def delete_info(id: int, response: Response):
    print(f"delete info request: {id=}")
    try:
        infos_manager.remove(id=id)
        return {"status": "deleted", "id": id}
    except psycopg.DatabaseError as error:
        print(error)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "failed"}


@router.get("/registered")
async def get_is_registered(labID: str):
    response = infos_manager.is_registered(labID)
    return "true" if response else "false"


@router.get("/lab-ids")
async def get_lab_ids():
    response = infos_manager.registered_rooms()
    return response


@router.patch("/lab-ids", status_code=status.HTTP_200_OK)
async def patch_lab_ids(request: RequestChange, response: Response):
    if sum((value[1] is not None) for value in request) != 2:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "You must specify either the 'id', 'identifier' or 'before_labID'; both cannot be omitted."
    elif request.after_labID is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "after_labID is required."
    elif (
        request.before_labID is not None
        and request.before_labID not in sender_manager.get_all_lab_id()
    ):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "before_labID does not exist."
    elif request.after_labID in sender_manager.get_all_lab_id():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "after_labID already exists."

    if request.id is not None:
        before = sender_manager.get_lab_id(request.id)
    elif request.identifier is not None:
        before = sender_manager.get_lab_id_from_identifier(request.identifier)
    else:
        before = request.before_labID

    if not before:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "requested sender is not found."

    try:
        sender_manager.change_lab_id(
            before_lab_id=before,
            after_lab_id=request.after_labID,
        )
        await ws_manager.send_change_lab_id(before, request.after_labID)
        return {"status": "labID changed."}
    except psycopg.DatabaseError as error:
        print(error)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "before_labID is an non-existent labID."


@router.get("/rooms")
async def get_active_rooms():
    response = ws_manager.active_rooms
    return response if response else "NoActiveRooms"


@router.post("/request", status_code=status.HTTP_200_OK)
async def post_request_info(request: RequestInfo, response: Response):
    print(f"receive request {request.labID}")
    if request.labID in ws_manager.active_rooms:
        await ws_manager.send_request_info(request.labID)
        response.status_code = status.HTTP_202_ACCEPTED
        return {"status": f"request sent to {request.labID}"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "non active room"}


@router.get("/get-rows")
async def get_rows(labID: str, rowLimit: int, descending: bool = True):
    response = infos_manager.get_rows(
        lab_id=labID, row_limit=rowLimit, descending=descending
    )
    return response


@router.get("/getInfo")
async def get_a_info(labID: str, date: str, numGen: int):
    response = infos_manager.select(lab_id=labID, date=date, num_gen=numGen)
    return response if response else "NoData"
