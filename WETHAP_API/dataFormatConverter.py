import sqlite3
from DBManage import DBCommands
from datetime import datetime

DB = DBCommands(DB_PATH = "./data.db")
newDB = DBCommands(DB_PATH = "./newdata.db")
newDB.createDB()
data = DB.previewData()

for datum in data:
    newDB.insert(
    labID = datum[0],
    date = datetime.strptime(datum[1], "%Y-%m-%d").strftime("%Y-%m-%d"),
    numGen = datum[2],
    temperature = datum[3],
    humidity = datum[4],
    pressure = datum[5],
    weather = datum[6]
    )

newDB.close()
DB.close()

print(data)
