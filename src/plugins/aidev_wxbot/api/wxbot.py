import os

import requests

from aidev_wxbot.api import Api, BkApi


class WxbotApi:
    def __init__(self):
        self.api = Api(os.getenv("WXBOT_URL"))

    def send(self, data, webhook):
        return self.api.call_action(f"send?key={webhook}", json=data, headers={"Content-Type": "application/json"})

    def replace_origin(self, data, response_code):
        return self.api.call_action(
            f"send?response_code={response_code}", json=data, headers={"Content-Type": "application/json"}
        )

    def get_chat(self, chat_url):
        res = requests.get(chat_url)
        return res.json()


class XworkBackendApi:
    def __init__(self):
        self.api = BkApi(os.getenv("XWORK_BACKEND_API_NAME"))

    def convert_to_rtx(self, userid_list: list):
        return self.api.call_action("convert_to_name", "POST", json={"userid_list": userid_list})
