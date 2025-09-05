import json
import logging
import os
from typing import Any, List

from pydantic import Field

from aidev_wxbot_plugin.api.wxbot import WxbotApi
from aidev_wxbot_plugin.context import Context, Message
from aidev_wxbot_plugin.context.message import MsgType

logger = logging.getLogger(__name__)


class WxWorkBotContext(Context):
    response_url: str = Field(default="")
    origin_dict: Any = Field(default={})
    group_members: List = Field(default=[])
    group_name: str = Field(default="")


class ContextGenerator:
    """
    分析原始信息，生成Context

    参看utils/context/__init__.py定义的Context类。
    """

    def __init__(self, payload: dict):
        self.payload = payload
        self.max_recursion = 3

    def generate(self) -> WxWorkBotContext:
        logger.info(f"企微传递的参数是 {json.dumps(self.payload, ensure_ascii=False)}")
        sender_id = self.payload.get("from", {}).get("alias") or self.payload.get("from", {}).get("name")
        sender_code = self.payload.get("from", {}).get("userid")
        from_type = self.payload.get("chattype")
        group_id = self.payload.get("chatid")
        chat_info_url = self.payload.get("getchatinfourl")
        chat_info = WxbotApi().get_chat(chat_info_url) if chat_info_url else {}
        logger.info(f"回调传递的群信息是 {json.dumps(chat_info, ensure_ascii=False)}")
        group_name = chat_info.get("name", "")
        ctx_data = {
            "from_type": from_type,
            "group_id": group_id,
            "sender_id": sender_id,
            "sender_code": sender_code,
            "group_members": chat_info.get("members", []),
            "group_name": group_name,
            "to_me": True,
            "origin_dict": self.payload,
        }

        ctx = WxWorkBotContext(**ctx_data)

        message = Message()
        message.response_url = self.payload.get("response_url")
        message.response_code = self.payload.get("response_url", "response_code=").split("response_code=")[-1]
        origin_msg_type = self.payload["msgtype"]
        ctx.message = getattr(self, f"_{origin_msg_type}_create")(message, self.payload, self.max_recursion)
        return ctx

    def _text_create(self, message: Message, payload: dict, recursion: int):
        content = payload["text"]["content"]
        message.msg_type = MsgType.Text.value
        rtx_name = os.getenv("RTX_NAME")
        if content.startswith(f"@{rtx_name}"):
            content = content[len(f"@{rtx_name}") :]
        message.text = content
        return message

    def _template_card_event_create(self, message: Message, payload: dict, recursion: int):
        message.msg_type = MsgType.Event.value
        message.event = "template_card_event"
        message.event_key = payload.get("template_card_event").get("event_key")
        message.text = payload.get("template_card_event").get("event_key", "").split("|")[0]
        return message

    def _attachment_create(self, message: Message, payload: dict, recursion: int):
        message.content = payload.get("attachment").get("callbackid")
        message.msg_type = MsgType.Event.value
        message.event_value = payload.get("attachment").get("actions").get("value")
        message.event_name = payload.get("attachment").get("actions").get("name")
        return message

    def _event_create(self, message: Message, payload: dict, recursion: int):
        message.msg_type = MsgType.Event.value
        message.event = payload.get("event").get("eventtype")
        message.text = payload.get("event").get("eventtype")
        return message

    def _component_action_create(self, message: Message, payload: dict, recursion: int):
        message.text = payload.get("action").get("value")
        message.msg_type = MsgType.Event.value
        message.event_value = self.payload.get("action").get("value")
        return message

    def _interaction_create(self, message: Message, payload: dict, recursion: int):
        message.text = self.payload.get("interaction", {}).get("report_data", "").split("|")[0]
        message.event_key = self.payload.get("interaction", {}).get("report_data", "")
        if payload.get("interaction", {}).get("input_json"):
            message.wxbot_interaction_json = json.loads(payload["interaction"]["input_json"])
        message.wxbot_interaction_text = payload.get("interaction").get("input_text")
        message.msg_type = MsgType.Event.value
        return message
