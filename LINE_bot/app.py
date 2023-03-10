# flask run
# sudo systemctl start nginxi
#

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

import pprint

app = Flask(__name__)

line_bot_api = LineBotApi('2kBmfbN8P9Rda5VaWC8th4KV8xcHW84xIMcl72P9k9AFFw07b5aZYbxH+hUOkG81nHt6ZKt9IDjShB9IDLrIWLoyjIuk8M5nSpRSYpPdIRjXvS4Cl7VRGq3EyeqbxS+qmyxXBmKtEW1GHLY3xYxq2wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('71ec82449abc71158b725a75a9ab3205')

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    pprint.pprint(event)
    
    text=event.message.text
    print(text)
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text))


if __name__ == "__main__":
    app.run()