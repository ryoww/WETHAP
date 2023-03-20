import requests
import json
from datetime import datetime

API_BASE_URL = "http://192.168.3.2/getInfo"

def fetchInfo(location: str, date: str, num_gen: int):
    inputURL = f"{API_BASE_URL}/?location={location}&year={datetime.now().year}&month={date.split('/')[0]}&day={date.split('/')[1]}&num_gen={num_gen}"
    response = requests.get(inputURL)
    fetchedData = json.loads(response.text)

    return fetchedData

if __name__ == "__main__":
    infoDict= fetchInfo("下沢家", "03/16", 8)

    print(infoDict)