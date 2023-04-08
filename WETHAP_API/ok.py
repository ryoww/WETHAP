from DBManage import DBCommands as db
db = db(DB_PATH = "./test.db")
print(db.select(labID = "みみみ", numGen = 3))
data = {
    "labID": "ややや",
    "numGen": 1,
    "temperature": 30.5,
    "humidity": 70.0,
    "pressure": 1013.0,
    "weather": "晴れ"
}

db.insert(
    labID = data["labID"],
    numGen = data["numGen"],
    temperature = data["temperature"],
    humidity = data["humidity"],
    pressure = data["pressure"],
    weather = data["weather"])

# db.insert(
#     labID = "ががが",
#     numGen = 1,
#     temperature = 1,
#     humidity = 2,
#     pressure = 3,
#     weather = "おい")

db.close()