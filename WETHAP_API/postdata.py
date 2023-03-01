import requests

URL = "http://127.0.0.1:8000/addInfo"

postInfo = {
    "temperature": 30.5,
    "humidity": 70.0,
    "pressure": 1013.0
}

response = requests.post(URL, postInfo)

print(response)