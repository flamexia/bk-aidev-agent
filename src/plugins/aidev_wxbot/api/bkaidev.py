from django.conf import settings

from aidev_wxbot.api import BkApi


class BkAiDevApi:
    def __init__(self):
        self.api = BkApi("bkaidev")

    def list_agent(self, username):
        return self.api.call_action("list_agent", "GET", params={"username": username})

    def retrieve_agent(self, agent_code):
        return self.api.call_action(f"openapi/aidev/resource/v1/agent/{agent_code}/", "GET")


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
