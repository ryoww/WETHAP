from flask import *

app = Flask(__name__)


# クエリなし、動作確認用に
@app.route("/", methods = ["GET"])
def root():

    return {"status": "online"}

    #例: http://127.0.0.1:8000


# 実際に情報を返すAPI
@app.route("/info/", methods = ["GET"])
def returnInfo():

    # クエリパラメータの取得
    lab = str(request.args.get("lab"))
    data = {
        "lab": lab
    }
    return data

    #例: http://127.0.0.1:8000/info/?lab=test


if __name__ == "__main__":

    # APIサーバを8000番ポートで起動
    app.run(port = 8000)