import datetime
import os

import dotenv
import requests

dotenv.load_dotenv()
URL = f"{os.environ.get('SERVER_URL')}{os.environ.get('PREFIX')}/addInfo"

postInfo = {
    "labID": "テスト研究室",
    # "date": str(datetime.date.today()),
    "numGen": 1,
    "temperature": 0,
    "humidity": 0,
    "pressure": 0,
}

response = requests.post(URL, json=postInfo)

print(response)
