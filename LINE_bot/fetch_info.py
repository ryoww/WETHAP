import requests
import json
from datetime import datetime

API_URL = "https://adelppi.duckdns.org/getInfo"
endTime = {
    1: "9:25",
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

def fetchInfo(location: str, date: str, num_gen: int):
    response = requests.get(API_URL)
    fetchedData = json.loads(response.text)
    inputDate = str(datetime.now().year) + "/" + date + "/" + endTime[num_gen]

    return (
        fetchedData[inputDate]["temperature"],
        fetchedData[inputDate]["humidity"],
        fetchedData[inputDate]["pressure"],
        fetchedData[inputDate]["wether"]
    )

if __name__ == "__main__":
    temperature, humidity, pressure, wether = fetchInfo("下沢家", "3/16", 8)

    print(
        temperature,
        humidity,
        pressure,
        wether
    )