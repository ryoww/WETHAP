import requests

URL = "http://127.0.0.1:8000/addInfo"

postInfo = {
    "labID": "テスト研究室",
    "date": "2023-1-1",
    "numGen": 1,
    "temperature": 0,
    "humidity": 0,
    "pressure": 0
}

response = requests.post(URL, json = postInfo)

print(response)