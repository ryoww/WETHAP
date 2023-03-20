# flask run
# ngrok http 5000

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from key import at, sk

import pprint
import re
from datetime import datetime
from fetch_info import fetchInfo

app = Flask(__name__)

line_bot_api = LineBotApi(at)
handler = WebhookHandler(sk)

@app.route("/", methods=['GET'])
def test():
    return "Hello"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# set situation
STATE_INITIAL = 0
STATE_LOCATION_RECEIVED = 1
STATE_DATE_RECEIVED = 2

# end time
endTime = {
    1: "9:25",
    2: "10:10",
    3: "11:10",
    4: "11:55",
    5: "13:30",
    6: "14:15",
    7: "15:15",
    8: "16:00",
    9: "17:00",
    10: "17:45",
    11: "18:45",
    12: "19:30"
    }

# lower limit date
mindate = datetime(2023,3,15).date()

# rooms list
rooms = ["下沢家"]

# process initial situation
def initial_state(event):

    text = "情報を知りたい研究室又は実験室を教えてください。"

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
    # change situation submitted location
    return STATE_LOCATION_RECEIVED

# process after submitted location
def location_received_state(event, location):

    if location in rooms:
        text = (f"{location}の情報を知りたい日付と実験時間を教えてください。(例:4月1日4限)")

        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
        # change initial situation
        return STATE_DATE_RECEIVED

    # if not registered location "plrease retype"
    else:
        text = "登録されている実験室又は研究室を入力ください。"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

        return STATE_LOCATION_RECEIVED

state = STATE_INITIAL
location = ""

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    global state, location, date, num_gen

    now = datetime.now()
    now_day = now.date()
    nowtime = now.time()

    print(event.message.text)

    if "教え" in event.message.text:
        # set initial state
        state = STATE_INITIAL
        location = ""
        state = initial_state(event)

    elif state == STATE_LOCATION_RECEIVED:
        # get location
        location = event.message.text
        state = location_received_state(event, location)

    elif state == STATE_DATE_RECEIVED:
        # try :
            # get day
            if "月" in event.message.text and "日" in event.message.text and "限" in event.message.text:

                text = event.message.text
                pattern = r"(\d{1,2}月\d{1,2}日)(\d+)限"
                match = re.search(pattern, text)
                date_str, class_num_str = match.groups()
                date = datetime.strptime(date_str, "%m月%d日").date().replace(year = now.year)
                num_gen = int(class_num_str)

                print(date)
                print(num_gen)
                endtime = datetime.strptime(endTime[num_gen],"%H:%M").time()



                if 1 > num_gen < 12:
                    text = "1~12限を入力してください"
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

                elif date > now_day:
                    text = "いつからWETHAPが未来を観測できると錯覚していた？もう一度入力しやがれ！！"
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

                elif date <= mindate:
                    text = "データがありません"
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

                elif date == now_day and endtime > nowtime:
                    text = "反映までもう少々お待ちください。"
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))


                else:
                    date = datetime.strftime(date, "%m/%d")
                    print(location)
                    print(date)
                    print(num_gen)
                    info = fetchInfo(location, date, num_gen)
                    T = info["temperature"]
                    H = info["humidity"]
                    AP = info["pressure"]
                    WE = info["weather"]
                    text = (f"{text}の{location}の情報は以下の通りです\n気温 : {T}℃\n湿度 : {H}%\n気圧 : {AP}hPa\n天気 : {WE}")
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

                    # set initial state
                    state = STATE_INITIAL
                    location = ""



            else :
                text = "正しく入力又は半角数字でしてください。あ"
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

        # except Exception as e:
        #     print(e)
        #     text = "正しく入力又は半角数字でしてください。"
        #     line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

    else:

        text = "「教えて」と入力すると情報を教えてくれます。場所を指定すると日付を聞かれます。日付を指定すると情報を返します。"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))


if __name__ == "__main__":
    app.run()