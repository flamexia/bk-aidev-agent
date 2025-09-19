from django.conf import settings

from aidev_wxbot.api import BkApi


class XworkBackendApi:
    def __init__(self):
        self.api = BkApi(settings.XWORK_BACKEND_API_NAME)

    def convert_to_rtx(self, userid_list: list):
        return self.api.call_action("convert_to_name", "POST", json={"userid_list": userid_list})
