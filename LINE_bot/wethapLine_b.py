import pprint
import re
import requests
import json
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


# process initial situation
def initial_state(event):

    text = "情報を知りたい研究室又は実験室を教えてください。"

    # change situation submitted location
    update_id_dict(event.source.user_id,state = STATE_LOCATION_RECEIVED)

    return text


# process after submitted location
def location_received_state(event, location):

    isRegistered = requests.get(f"https://adelppi.duckdns.org/isRegistered/?labID={location}").text

    if isRegistered == "True":
        update_id_dict(event.source.user_id,state = STATE_DATE_RECEIVED,location = location)


        text = (f"{location}の情報を知りたい日付と実験時間を教えてください。(例:4月1日4限)")

        return text

    # if not registered location "plrease retype"
    else:
        text = "登録されている実験室又は研究室を入力ください。"

        return text


id_dict = {}

def update_id_dict(id,**update_data):
    if id in id_dict.keys():
        for key, value in update_data.items():
            id_dict[id][key] = value
    else:
        print(f"{id} not found")


def delete_data(id):
    if id in id_dict.keys():
        del id_dict[id]
    else:
        print(f"{id} not found")


def add_data(id,**new_data):
    if id in id_dict.keys():
        print(f"{id} already exists")
    else:
        id_dict[id] = new_data


# every week send
every_week_dict = {}
def register_id(id,**new_data):
    if id in every_week_dict.keys():
        print(f"{id} already exists")
    else:
        every_week_dict[id] = new_data


state = STATE_INITIAL
location = ""


def handle_text(event):
    global state, location, date, num_gen

    print(state)

    now = datetime.now()
    now_day = now.date()
    nowtime = now.time()

    pprint.pprint(event)
    print(event)
    print(event.message.text)
    print(event.source.user_id)
    # print(event)

    print(id_dict)

    if "!登録" in event.message.text:
        register_id(event.source.user_id,)

    if "教え" in event.message.text:
        # set inital state and register id
        if str(event.source.user_id) not in id_dict.keys():
            add_data(event.source.user_id,state = STATE_INITIAL,location = "")

        # set initial state
        initial_state(event)


    # elif id_dict.get(event.source.user_id,dict()).get(state) == STATE_LOCATION_RECEIVED:
    elif str(event.source.user_id) in id_dict.keys() and id_dict[event.source.user_id]["state"] == STATE_LOCATION_RECEIVED:
        # get location
        location = event.message.text
        location_received_state(event, location)

    # elif state == STATE_DATE_RECEIVED:
    elif str(event.source.user_id) in id_dict.keys() and id_dict[event.source.user_id]["state"] == STATE_DATE_RECEIVED:
        try :
            # get day
            if "月" in event.message.text and "日" in event.message.text and "限" in event.message.text:

                text = event.message.text
                pattern = r"(\d{1,2}月\d{1,2}日)(\d+)限"
                match = re.search(pattern, text)
                date_str, class_num_str = match.groups()
                date = datetime.strptime(date_str, "%m月%d日").date().replace(year = now.year)
                num_gen = int(class_num_str)

                print(date)
                endtime = datetime.strptime(endTime[num_gen],"%H:%M").time()
                update_id_dict(event.source.user_id,date = date)


                if 1 > num_gen < 12:
                    text = "1~12限を入力してください"

                    return text

                elif date > now_day:
                    text = "いつからWETHAPが未来を観測できると錯覚していた？もう一度入力しやがれ！！"

                    return text

                # elif date < mindate:
                #     text = "データがありません"
                #     line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

                elif date == now_day and endtime > nowtime:
                    text = "反映までもう少々お待ちください。"

                    # set initial state
                    delete_data(event.source.user_id)

                    return text

                else:
                        # 4/1~submit
                        if 3 >= now.month >= 1 and 12 >= date.month >= 4:
                            date.replace(year =  now.year - 1)

                        location = str(id_dict[event.source.user_id]["location"])
                        print(location)
                        info = fetchInfo(location, date, num_gen)
                        T = info["temperature"]
                        H = info["humidity"]
                        AP = info["pressure"]
                        WE = info["weather"]
                        text = (f"{date.year}年{text}の{location}の情報は以下の通りです\n気温 : {T}℃\n湿度 : {H}%\n気圧 : {AP}hPa\n天気 : {WE}")

                        # set initial state
                        delete_data(event.source.user_id)
                        print(id_dict)

                        return text


            else :
                text = "正しく入力又は半角数字でしてください。あ"
                return text

        except Exception as e:
            print(e)
            text = "正しく入力又は半角数字でしてください。"
            return text

    else:

        text = "「教えて」と入力すると情報を教えてくれます。場所を指定すると日付を聞かれます。日付を指定すると情報を返します。"
        return text