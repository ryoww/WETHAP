import json

from linebot import LineBotApi
from linebot.models import TextSendMessage

from key import ats


def load_json():
    with open("every_week_send.json", "r") as file:
        user_dict = json.load(file)
    return user_dict





line_bot_api = [LineBotApi(at) for at in ats]

def main():
    user_id = "user_id"

    text = ""

    line_bot_api[3].push_message(user_id, TextSendMessage(text))
