import re
import requests
import json

from datetime import datetime
from fetch_info import fetchInfo


# set situation
STATE_LOCATION_RECEIVED = 0
STATE_DATE_RECEIVED = 1


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
        user_dict = json.load(file)
    return user_dict


def load_every_json():
    with open("every_week_send.json", "r") as file:
        user_dict = json.load(file)
    return user_dict


def write_json(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


def write_every_json(data):
    with open("every_week_send.json", "w") as file:
        json.dump(data, file, indent=4)


def delete_json(id):
    user_dict = load_json()

    del user_dict[id]

    write_json(user_dict)


def delete_every_json(id):
    user_dict = load_every_json()

    del user_dict[id]

    write_every_json(user_dict)


def update_data(id, **new_data):
    user_dict = load_json()

    if id in user_dict.keys():
        for key, value in new_data.items():
            user_dict[id][key] = value

        write_json(user_dict)


def update_every_data(id, **new_data):
    user_dict = load_every_json()

    if id in user_dict.keys():
        for key, value in new_data.items():
            user_dict[id][key] = value
        write_json(user_dict)


def add_id_data(id, **new_data):
    user_dict = load_json()

    user_dict[id] = new_data

    write_json(user_dict)



def register_user_dict(event):
    user_dict = load_json()

    if event.source.user_id not in user_dict.keys():
        add_id_data(event.source.user_id, state=STATE_LOCATION_RECEIVED)

        text = "情報を知りたい研究室又は実験室を教えてください。"

        return text

    else:
        # reset user_id
        delete_json(event.source.user_id)

        add_id_data(event.source.user_id, STATE_LOCATION_RECEIVED)

        text = "情報を知りたい研究室又は実験室を教えてください。"

        return text


def register_every_week_user(event):
    user_dict = load_every_json()

    if event.source.user_id in user_dict.keys():
        text = ""


# process after submitted location
def location_received_state(event):
    location = event.message.text

    # request API
    isRegisterd = requests.get(f"https://adelppi.duckdns.org/isRegistered/?labID={location}").text

    if isRegisterd == "True":
        update_data(event.source.user_id, state = STATE_DATE_RECEIVED, location = str(location))

        text = (f"{location}の情報を知りたい日付と実験時間を教えてください。(例:4月1日4限)")

        return text

    # if not registered location, reply "please retype location"
    else:
        text = "登録されている実験室又は研究室を入力ください。"

        return text


# last process
def date_numgen_received_state(event):
    # set time
    now = datetime.now()

    try:
        # get day
        if "月" in event.message.text and "日" in event.message.text and "限" in event.message.text:
            pattern = r"(\d{1,2}月\d{1,2}日)(\d+)限"
            match = re.search(pattern, text)
            date_str, num_gen_str = match.groups()

            date = datetime.strptime(date_str, "%m月%d日").date().replace(year=now.year)
            num_gen = int(num_gen_str)

            end_time = datetime.strptime(endTime[num_gen], "%H:%M").time()
            update_data(event.source.user_id, date=date)

            if 1 > num_gen < 12:
                text = "1 ~ 12限を入力してください"

                return text

            elif now.date() < date:
                text = "WETHAPは未来を観測できません。"

                return text

            elif date == now.date() and now.time() < end_time:
                text = "反映までもう少々お待ちください。"

                # delete user_id
                delete_json(event.source.user_id)

                return text

            else:
                if 1 <= now.month <= 3 and 4 <= date.month <= 12:
                    date.replace(year=now.year - 1)

                user_dict = load_json()

                location = user_dict[event.source.user_id]["location"]
                info = fetchInfo(location, date, num_gen)
                T = info["temperature"]
                H = info["humidity"]
                AP = info["pressure"]
                WE = info["weather"]
                text = (f"{date.year}年{text}の{location}の情報は以下の通りです\n気温 : {T}℃\n湿度 : {H}%\n気圧 : {AP}hPa\n天気 : {WE}")

                # delete user_id
                delete_json(event.source.user_id)

                return text

    except Exception:
        text = "正しく入力又は半角数字で入力してください"

        return text


# impoted func by app.py
def handle_text(event):

    user_dict = load_json()

    # first section
    if "教え" in event.message.text:
        text = register_user_dict(event)

        return text


    # second section
    elif user_dict[event.source.user_id]["state"] == STATE_LOCATION_RECEIVED:
        text = location_received_state(event)

        return text


    # third section
    elif user_dict[event.source.user_id]["state"] == STATE_DATE_RECEIVED:
        text = date_numgen_received_state(event)

        return text


    if "登録" in event.message.text:
        text = register_every_week_user(event)

        return text


    # if didn't match conditions
    else:
        text = "「教えて」と入力すると情報を教えてくれます。場所を指定すると日付を聞かれます。日付を指定すると情報を返します。"

        return text