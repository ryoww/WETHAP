import requests
import json
from datetime import datetime
from datetime import date

API_BASE_URL = "https://adelppi.duckdns.org/getInfo"

# dateをyyyy/mm/ddの形で渡してdate.year,date.month,date.dayで分ける方がいい？
def fetchInfo(location, date, num_gen):
    inputURL = f"{API_BASE_URL}/?labID={location}&date={date.year}-{date.month}-{date.day}&numGen={num_gen}"
    print(inputURL)
    response = requests.get(inputURL)
    fetchedData = json.loads(response.text)

    return fetchedData

if __name__ == "__main__":
    date = date(2023,4,3)
    print(date)
    infoDict= fetchInfo("下沢家", date , 1)

    print(infoDict)