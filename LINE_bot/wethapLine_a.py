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


def register_data(id, state, location, num_gen):
    data = load_json()

    new_data = {id : {
                        "state" : state,
                        "location" : location,
                        "num_gen" : num_gen
                }}

    data.update(new_data)

    write_json(data)


def initial_step(event):
    text = "情報を知りたい研究室又は実験室教えてください"

    return 

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
            register_data(event.source.user_id, STATE_INITIAL, "")

        initial_step(event)