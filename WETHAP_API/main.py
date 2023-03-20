from flask import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


@app.route("/", methods = ["GET"])
def root():
    return {"status": "online"}


@app.route("/addInfo/", methods = ["POST"])
def addInfo():
    return "added"


@app.route("/getInfo/", methods = ["GET"])
def getInfo():
    return "a"


if __name__ == "__main__":
    app.run(port = 8000)