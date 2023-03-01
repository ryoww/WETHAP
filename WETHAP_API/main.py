from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.labInfo"
db = SQLAlchemy(app)
ma = Marshmallow(app)


class LabInfo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    time = db.Column(db.DateTime, default = datetime.now)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)


@app.route("/", methods = ["GET"])
def root():
    return {"status": "online"}


class LabInfoSchema(ma.Schema):
    class Meta:
        fields = ("id", "time", "temperature", "humidity", "pressure")


labInfosSchema = LabInfoSchema(many = True)


@app.route("/addInfo/", methods = ["POST"])
def addInfo():
    temperature = request.form.get("temperature")
    humidity = request.form.get("humidity")
    pressure = request.form.get("pressure")

    labInfo = LabInfo(temperature = temperature,
                    humidity = humidity,
                    pressure = pressure)

    db.session.add(labInfo)
    db.session.commit()

    return "added"


@app.route("/getInfo/", methods = ["GET"])
def getInfo():
    allLabInfo = LabInfo.query.all()
    result = labInfosSchema.dump(allLabInfo)

    return jsonify(result)


if __name__ == "__main__":
    db.create_all()
    app.run(port = 8000)