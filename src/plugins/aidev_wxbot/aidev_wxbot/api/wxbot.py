from aidev_wxbot.api import Api
from django.conf import settings


class XworkBackendApi:
    def __init__(self):
        self.api = Api(settings.XWORK_BACKEND_API_URL)

    @property
    def access_token(self):
        return self.api.call_action(f"/gettoken?corpid={settings.CORPID}&corpsecret={settings.CORPSECRET}")[
            "access_token"
        ]

    def get_user_info(self, user_id):
        return self.api.call_action(f"/user/get?access_token={self.access_token}&userid={user_id}", "GET")
