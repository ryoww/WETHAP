import re
import requests
import json
import pprint


from datetime import datetime
from datetime import date
from fetch_info import fetchInfo


# set situation
STATE_INITIAL = 0
STATE_LOCATION_RECEIVED = 1
STATE_DATE_RECEIVED = 2


# end time
endTime = {
    1 : "09:25",
    2 : "10:10",
    3 : "11:10",
    4 : "11:55",
    5 : "13:30",
    6 : "14:15",
    7 : "15:15",
    8 : "16:00",
    9 : "17:00",
    10: "17:45",
    11: "18:45",
    12: "19:30"
    }


def load_json():
    with open("data.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


def delete_json(id):
    data = load_json()

    del data[id]

    write_json(data)

def register_data(id, **new_data):
    data = load_json()

    if id in data.keys():
        return "already exisits"

    else :
        data[id] = new_data

        write_json(data)


def update_data(id, **new_data):
    data = load_json()

    if id in data.keys():
        for key, value in new_data.items():
            data[id][key] = value

        write_json(data)


# process after submitted location
def location_received_state(event, location):

    # request API
    isRegisterd = requests.get(f"https://adelppi.duckdns.org/isRegistered/?labID={location}").text

    if isRegisterd == "True":
        update_data(event.source.user_id, state = STATE_DATE_RECEIVED, location = location)

        text = (f"{location}の情報を知りたい日付と実験時間を教えてください。(例:4月1日4限)")

        return text

    # if not registered location, reply "please retype location"
    else:
        text = "登録されている実験室又は研究室を入力ください。"

        return text


def handle_text(event):
    # set time
    now = datetime.now()
    now_day = now.date()
    now_time = now.time()

    user_dict = load_json()

    # if "教え" in message, register id
    if "教え" in event.message.text:

        # set initial state and register id
        if str(event.source.user_id) not in user_dict.keys():
            register_data(event.source.user_id, state = STATE_INITIAL, location = "")

        update_data(event.source.user_id, state = STATE_LOCATION_RECEIVED)

        return "情報を知りたい研究室又は実験室教えてください"


    elif user_dict[event.source.user_id]["state"] == STATE_LOCATION_RECEIVED:
        text = location_received_state(event.source.user_id, event.message.text)

        return text