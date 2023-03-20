import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost/getInfo"

def fetchInfo(location: str, date: str, num_gen: int):
    inputURL = API_BASE_URL + "/?location=高専&year=2023&month=03&day=16&num_gen=8"
    response = requests.get(inputURL)
    fetchedData = json.loads(response.text)

    return fetchedData

if __name__ == "__main__":
    infoDict= fetchInfo("下沢家", "3/16", 8)

    print(infoDict)