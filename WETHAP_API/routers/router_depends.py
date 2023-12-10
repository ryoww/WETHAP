import datetime

from pydantic import BaseModel


class Info(BaseModel):
    labID: str
    date: str = str(datetime.date.today())
    numGen: int = None
    temperature: float
    humidity: float
    pressure: float
