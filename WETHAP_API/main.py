from flask import *
from flask_cors import CORS
from datetime import datetime
from DBManage import DBCommands
from fetchWeather import fetchWeather
import json

app = Flask(__name__)
CORS(app, supports_credentials = True)

PREFIX = "/WETHAP/api"

@app.route(PREFIX + "/", methods = ["GET"])
def index():
    return {"status":"online"}


@app.route(PREFIX + "/addInfo/", methods = ["POST"])
def addInfo():
    db = DBCommands(DB_PATH = "./data.db")
    data = request.get_json()
    db.insert(
        labID = data["labID"],
        numGen = data["numGen"],
        date = datetime.now().strftime("%Y-%m-%d"),
        temperature = data["temperature"],
        humidity = data["humidity"],
        pressure = data["pressure"],
        weather = fetchWeather())
    db.close()
    print(request)
    return "added"


@app.route(PREFIX + "/isRegistered/", methods = ["GET"])
def isRegistered():
    db = DBCommands(DB_PATH = "./data.db")
    labID = str(request.args.get("labID"))
    isRegistered = db.isRegistered(labID = labID)
    db.close()

    return str(isRegistered)

@app.route(PREFIX + "/registeredRooms/", methods = ["GET"])
def registeredRooms():
    db = DBCommands(DB_PATH = "./data.db")
    data = db.registeredRooms()
    db.close()

    return data

@app.route(PREFIX + "/previewData/", methods = ["GET"])
def previewData():
    db = DBCommands(DB_PATH = "./data.db")
    data = db.previewData()
    db.close()

    return data


@app.route(PREFIX + "/getInfo/", methods = ["GET"])
def getInfo():
    db = DBCommands(DB_PATH = "./data.db")
    labID = str(request.args.get("labID"))
    date = datetime.strptime(str(request.args.get("date")), "%Y-%m-%d").strftime("%Y-%m-%d")
    numGen = int(request.args.get("numGen"))
    data = db.select(labID = labID, date = date, numGen = numGen)
    db.close()

    if data is not None:
        return {
            "labID": data[0],
            "date": data[1],
            "numGen": data[2],
            "temperature": data[3],
            "humidity": data[4],
            "pressure": data[5],
            "weather": data[6]
        }
    else: 
        return "NODATA"


if __name__ == "__main__":
    app.run(port = 8000)
