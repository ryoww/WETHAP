import asyncio
import datetime
import json
import os

import dotenv
import requests
import websockets

dotenv.load_dotenv()


def post():
    URL = f"http://solithv7247.duckdns.org{os.environ.get('PREFIX')}/addInfo/"
    URL = f"http://127.0.0.1:{os.environ.get('SERVER_PORT')}{os.environ.get('PREFIX')}/addInfo/"

    postInfo = {
        "labID": "テスト研究室",
        # "date": str(datetime.date.today()),
        # "numGen": 1,
        "temperature": 0,
        "humidity": 0,
        "pressure": 0,
    }

    response = requests.post(URL, json=postInfo)

    print(response, response.text)


async def main():
    URL = f"wss://solithv7247.duckdns.org{os.environ.get('PREFIX')}/ws"
    # URL = f"ws://127.0.0.1:{os.environ.get('SERVER_PORT')}{os.environ.get('PREFIX')}/ws"

    async with websockets.connect(URL) as websocket:
        print("connected")
        await websocket.send(json.dumps({"uuid": "test", "labID": "テスト研究室"}))
        labID = await websocket.recv()
        labID = json.loads(labID)["labID"]
        print(labID)
        while True:
            # response = await websocket.recv()
            # response = json.loads(response)
            # if response["message"] == "request info":
            #     message = {
            #         "labID": labID,
            #         # "date": str(datetime.date.today()),
            #         "numGen": response["numGen"],
            #         "temperature": 0.0,
            #         "humidity": 0.0,
            #         "pressure": 0.0,
            #     }
            #     await websocket.send(json.dumps(message))
            #     print(f"Sent from Client: {message}")
            message = {
                "labID": labID,
                # "date": str(datetime.date.today()),
                # "numGen": 1,
                "temperature": 0.0,
                "humidity": 0.0,
                "pressure": 0.0,
            }
            await websocket.send(json.dumps(message))
            print(f"Sent from Client: {message}")


async def ping_pong():
    URL = f"ws://127.0.0.1:8000{os.environ.get('PREFIX')}/ws/PingPong"

    async with websockets.connect(URL) as websocket:
        print("connected")
        await websocket.send("ping")
        print("send ping")
        response = await websocket.recv()
        print(f"received message: {response}")


if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_until_complete(ping_pong())
    # post()
