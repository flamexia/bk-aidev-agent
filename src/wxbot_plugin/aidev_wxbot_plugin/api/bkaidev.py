from django.conf import settings

from aidev_wxbot_plugin.api import BkApi


class BkAiDevApi:
    def __init__(self):
        self.api = BkApi("bkaidev")

    def list_space(self, username):
        pass

    def get_space(self, space_id):
        pass

    def list_agent(self, username):
        pass

    def get_agent(self, agent_id):
        pass


class AgentBackend:
    def __init__(self):
        self.api = BkApi(settings.BKPAAS_BK_PLUGIN_APIGW_NAME)

    def invoke(self, content):
        data = {
            "inputs": {
                "command": "chat",
                "input": content,
                "stream": False,
                "chat_history": [{"role": "user", "content": content}],
                "context": [],
            },
            "context": {"executor": "user"},
        }
        return self.api.call_action("invoke/1.0.0assistant", "POST", json=data)
