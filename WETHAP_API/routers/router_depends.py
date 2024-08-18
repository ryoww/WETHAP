import datetime

from pydantic import BaseModel


class Info(BaseModel):
    labID: str
    date: str = str(datetime.date.today())
    time: str = None
    numGen: int = None
    temperature: float
    humidity: float
    pressure: float


class RequestInfo(BaseModel):
    labID: str
    standby_sec: int = 5


class RequestChange(BaseModel):
    id: int | None = None
    identifier: str | None = None
    before_labID: str | None = None
    after_labID: str
