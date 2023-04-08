from flask import *
from datetime import datetime
from DBManage import DBCommands
import json

app = Flask(__name__)
# db = db(DB_PATH = "./test.db")

endTime = {
    1: "09:25",
    2: "10:10",
    3: "11:10",
    4: "11:55",
    5: "13:30",
    6: "14:15",
    7: "15:15",
    8: "16:00",
    9: "17:00",
    10: "17:45",
    11: "18:45",
    12: "19:30"
    }

@app.route("/", methods = ["GET"])
def root():
    return {"status": "online"}


@app.route("/addInfo/", methods = ["POST"])
def addInfo():
    db = DBCommands(DB_PATH = "./test.db")
    data = request.get_json()
    print(data)

    # data = {
    #     "labID": "ややや",
    #     "numGen": 1,
    #     "temperature": 30.5,
    #     "humidity": 70.0,
    #     "pressure": 1013.0,
    #     "weather": "晴れ"
    # }

    db.insert(
        labID = data["labID"],
        numGen = data["numGen"],
        temperature = data["temperature"],
        humidity = data["humidity"],
        pressure = data["pressure"],
        weather = data["weather"])

    # db.insert(
    #     labID = "ういういうい",
    #     numGen = 1,
    #     temperature = 1,
    #     humidity = 2,
    #     pressure = 3,
    #     weather = "おい")
    db.close()

    return "added"


# @app.route("/getInfo/", methods = ["GET"])
# def getInfo():
#     location = str(request.args.get("location"))
#     year = str(request.args.get("year"))
#     month = str(request.args.get("month"))
#     day = str(request.args.get("day"))
#     num_gen = int(request.args.get("num_gen"))

#     # monthPrefix = "0" + month if len(month) == 1 else month
#     # dayPrefix = "0" + day if len(day) == 1 else day
#     key = f"{year}/{month}/{day}/{endTime[num_gen]}"

#     jsonPath = "./test.json"

#     with open(jsonPath, "r") as file:
#         jsonContent = json.load(file)

#     return jsonContent[key]


if __name__ == "__main__":
    app.run(port = 8000)