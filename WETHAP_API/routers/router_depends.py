import datetime

from pydantic import BaseModel


class Info(BaseModel):
    labID: str
    date: str = str(datetime.date.today())
    numGen: int = None
    temperature: float
    humidity: float
    pressure: float


class RequestInfo(BaseModel):
    labID: str


class RequestChange(BaseModel):
    id: int | None = None
    before_labID: str | None = None
    after_labID: str
