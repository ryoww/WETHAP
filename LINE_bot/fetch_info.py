import requests
import json
from datetime import datetime
from datetime import date

API_BASE_URL = "https://solithv7247.duckdns.org/WETHAP/api/getInfo/"

# dateをyyyy/mm/ddの形で渡してdate.year,date.month,date.dayで分ける方がいい？
def fetchInfo():
    now = datetime.now()

    inputURL = f"{API_BASE_URL}?labID=ラズパイカフェ&date={now.year}-{now.month}-{now.day}"
    print(inputURL)
    response = requests.get(inputURL)
    info = json.loads(response.text)

    T = info["temperature"]
    H = info["humidity"]
    AP = info["pressure"]
    WE = info["weather"]
    text = (f"{now.year}年{now.month}月{now.day}日{now.hour}時{now.minute}分のラズパイカフェの情報は以下の通りです\n気温 : {T}℃\n湿度 : {H}%\n気圧 : {AP}hPa\n天気 : {WE}")

    return text

if __name__ == "__main__":
    print(date)
    infoDict= fetchInfo()

    print(infoDict)