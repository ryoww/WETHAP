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
import datetime

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


# process initial situation
def initial_state(event):

    # 後で登録されてない場所だったらstate_initalに変更

    text = "情報を知りたい研究室又は実験室を教えてください。"

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
    # change situation submitted location
    return STATE_LOCATION_RECEIVED

# process after submitted location
def location_received_state(event, location):
    text = (f"{location}の情報を知りたい日付を教えてください。(例:4月1日)")

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
    # change initial situation
    return STATE_DATE_RECEIVED

state = STATE_INITIAL
location = ""

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    global state, location

    if event.message.text == "教えて":
        # set initial state
        state = STATE_INITIAL
        location = ""
        state = initial_state(event)

    elif state == STATE_LOCATION_RECEIVED:
        # get location
        location = event.message.text
        state = location_received_state(event, location)

    elif state == STATE_DATE_RECEIVED:
        # get day
        if "月" in event.message.text and "日" in event.message.text:
            date_str = event.message.text
            date = datetime.datetime.strptime(date_str, "%m月%d日")
            info = get_information(location, date)

            text = (f"{date_str}の{location}の情報は以下の通りです")
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

            # set initial state
            state = STATE_INITIAL
            location = ""

        else:

            text = "「教えて」と入力すると情報を教えてくれます。場所を指定すると日付を聞かれます。日付を指定すると情報を返します。"

            line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

def get_information(location, date):

    return "情報"

if __name__ == "__main__":
    app.run()