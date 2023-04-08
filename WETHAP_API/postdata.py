import requests

URL = "http://127.0.0.1:8000/addInfo"

postInfo = {
    "labID": "ややや",
    "numGen": 1,
    "temperature": 30.5,
    "humidity": 70.0,
    "pressure": 1013.0,
    "weather": "晴れ"
}

response = requests.post(URL, postInfo)

print(response)