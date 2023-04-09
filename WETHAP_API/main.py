from flask import *
from datetime import datetime
from DBManage import DBCommands
import json

app = Flask(__name__)


@app.route("/", methods = ["GET"])
def root():

    return {"status": "online"}


@app.route("/addInfo/", methods = ["POST"])
def addInfo():
    db = DBCommands(DB_PATH = "./data.db")
    data = request.get_json()
    db.insert(
        labID = data["labID"],
        numGen = data["numGen"],
        date = data["date"],
        temperature = data["temperature"],
        humidity = data["humidity"],
        pressure = data["pressure"],
        weather = data["weather"])
    db.close()

    return "added"


@app.route("/getInfo/", methods = ["GET"])
def getInfo():
    db = DBCommands(DB_PATH = "./data.db")
    labID = str(request.args.get("labID"))
    date = str(request.args.get("date"))
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