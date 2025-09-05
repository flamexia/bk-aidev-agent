import uuid

from aidev_wxbot_plugin.context.message import MsgType
from aidev_wxbot_plugin.wxaibot.context import WxWorkAiBotContext
from aidev_wxbot_plugin.wxaibot.plugins import register_plugin


def get_return_task_id(context: WxWorkAiBotContext):
    if context.message.msg_type == MsgType.Event.value:
        return context.message.wxaibot_template_card_event["task_id"]
    else:
        return uuid.uuid4().hex


@register_plugin("welcome", ["1", "help", "帮助"])
def welcome(current_context: WxWorkAiBotContext):
    return {
        "msgtype": "stream_with_template_card",
        "template_card": {
            "card_type": "button_interaction",
            "source": {"desc": "bkchat智能体", "desc_color": 0},
            "main_title": {
                "title": "欢迎使用bkchat智能体",
                "desc": f"{current_context.sender_id},您正在使用bkchat智能体！",
            },
            "sub_title_text": "请选择一个智能体空间",
            "button_selection": {
                "question_key": "bind_space",
                "title": "智能体空间",
                "disable": False,
                "option_list": [{"id": "wzry", "text": "王者荣耀"}, {"id": "lol", "text": "英雄联盟"}],
                "selected_id": "space_id",
            },
            "button_list": [
                {"text": "确认", "style": 4, "key": "bind_space"},
                {"text": "下一页", "style": 4, "key": "list_space|2"},
            ],
            "task_id": get_return_task_id(current_context),
        },
    }


@register_plugin("list_space")
def list_space(current_context: WxWorkAiBotContext):
    _, space_page = current_context.message.event_key.split("|")
    space_page = int(space_page)
    return {
        "response_type": "update_template_card",
        "template_card": {
            "card_type": "button_interaction",
            "source": {"desc": "bkchat智能体", "desc_color": 0},
            "main_title": {
                "title": "欢迎使用bkchat智能体",
                "desc": f"{current_context.sender_id},您正在使用bkchat智能体！",
            },
            "sub_title_text": "请选择一个智能体空间",
            "button_selection": {
                "question_key": "bind_space",
                "title": "智能体空间",
                "disable": False,
                "option_list": [{"id": "bns", "text": "剑灵"}, {"id": "tt", "text": "天堂"}],
                "selected_id": "space_id",
            },
            "button_list": [
                {"text": "确认", "style": 4, "key": "bind_space"},
                {"text": "下一页", "style": 4, "key": "list_space|2"},
            ],
            "task_id": get_return_task_id(current_context),
        },
    }


@register_plugin("bind_space", [])
def bind_space(current_context):
    bind_space_id = current_context.message.wxaibot_template_card_event["selected_items"]["selected_item"][0][
        "option_ids"
    ]["option_id"][0]
    return {
        "response_type": "update_template_card",
        "template_card": {
            "card_type": "button_interaction",
            "source": {"desc": "bkchat智能体", "desc_color": 0},
            "main_title": {
                "title": "欢迎使用bkchat智能体",
                "desc": f"{current_context.sender_id},您已经绑定了空间{bind_space_id}！",
            },
            "sub_title_text": "请选择一个智能体agent！",
            "button_selection": {
                "question_key": "bind_agent",
                "title": "智能体agent",
                "disable": False,
                "option_list": [{"id": "troubleshooting", "text": "故障处理"}, {"id": "qa", "text": "智能问答"}],
                "selected_id": "agent_id",
            },
            "button_list": [
                {"text": "确认", "style": 4, "key": "bind_agent"},
                {"text": "下一页", "style": 4, "key": "list_agent|2"},
            ],
            "task_id": get_return_task_id(current_context),
        },
    }


@register_plugin("list_agent", [])
def list_agent(current_context):
    bind_space_id = "lol"
    return {
        "response_type": "update_template_card",
        "template_card": {
            "card_type": "button_interaction",
            "source": {"desc": "bkchat智能体", "desc_color": 0},
            "main_title": {
                "title": "欢迎使用bkchat智能体",
                "desc": f"{current_context.sender_id},您已经绑定了空间{bind_space_id}！",
            },
            "sub_title_text": "请选择一个智能体agent！",
            "button_selection": {
                "question_key": "bind_agent",
                "title": "智能体agent",
                "disable": False,
                "option_list": [{"id": "troubleshooting", "text": "故障处理"}, {"id": "qa", "text": "智能问答"}],
                "selected_id": "agent_id",
            },
            "button_list": [
                {"text": "确认", "style": 4, "key": "bind_agent"},
                {"text": "下一页", "style": 4, "key": "list_agent|2"},
            ],
            "task_id": get_return_task_id(current_context),
        },
    }


@register_plugin("bind_agent", [])
def bind_agent(payload):
    pass
