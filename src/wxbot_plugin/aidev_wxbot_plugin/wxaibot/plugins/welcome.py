import uuid

from django.conf import settings

from aidev_wxbot_plugin.api.bkaidev import BkAiDevApi
from aidev_wxbot_plugin.context.message import MsgType
from aidev_wxbot_plugin.wxaibot.context import WxWorkAiBotContext, stream_msg
from aidev_wxbot_plugin.wxaibot.models import SessionAgentBinding
from aidev_wxbot_plugin.wxaibot.plugins import register_plugin


def get_return_task_id(context: WxWorkAiBotContext):
    if context.message.msg_type == MsgType.Event.value:
        return context.message.wxaibot_template_card_event["task_id"]
    else:
        return uuid.uuid4().hex


@register_plugin("welcome", ["1", "help", "帮助"])
def welcome(current_context: WxWorkAiBotContext):
    if settings.IS_INDEPENDENT_BOT:
        # agent_code = settings.BKPAAS_APP_CODE
        agent_code = "ai-devwxbot-test"
        agent_info = BkAiDevApi().retrieve_agent(agent_code)
        return stream_msg(f"欢迎使用智能体{agent_info['agent_name']}", True, get_return_task_id(current_context))
    else:
        if not SessionAgentBinding.objects.filter(
            sender=current_context.sender_code, group_id=current_context.group_id
        ).exists():
            all_agents = BkAiDevApi().list_agent(current_context.sender_id)[:10]
            option_list = [{"id": agent["agent_code"], "text": agent["agent_name"]} for agent in all_agents]
            return {
                "msgtype": "stream_with_template_card",
                "template_card": {
                    "card_type": "button_interaction",
                    "source": {"desc": "bkchat智能体", "desc_color": 0},
                    "main_title": {
                        "title": "欢迎使用bkchat智能体",
                        "desc": f"{current_context.sender_id},您正在使用bkchat智能体！",
                    },
                    "sub_title_text": "请绑定一个智能体！",
                    "button_selection": {
                        "question_key": "bind_agent",
                        "title": "有权限的智能体",
                        "disable": False,
                        "option_list": option_list,
                        "selected_id": "agent_id",
                    },
                    "button_list": [
                        {"text": "确认", "style": 4, "key": f"bind_agent|{current_context.sender_id}"},
                        {"text": "下一页", "style": 4, "key": f"list_agent|2|{current_context.sender_id}"},
                    ],
                    "task_id": get_return_task_id(current_context),
                },
            }
        else:
            session_agent_binding = SessionAgentBinding.objects.get(
                sender=current_context.sender_code, group_id=current_context.group_id
            )
            return stream_msg(
                f"欢迎使用bkchat智能体，当前你已经绑定了{session_agent_binding.agent_name}",
                True,
                get_return_task_id(current_context),
            )


@register_plugin("list_agent")
def list_agent(current_context: WxWorkAiBotContext):
    _, space_page, sender_id = current_context.message.event_key.split("|")
    if sender_id != current_context.sender_id:
        return stream_msg("不能点击别人唤起的会话！", True, get_return_task_id(current_context))
    space_page = int(space_page)
    all_agents = BkAiDevApi().list_agent(current_context.sender_id)[(space_page - 1) * 10 : space_page * 10]
    option_list = [{"id": agent["agent_code"], "text": agent["agent_name"]} for agent in all_agents]
    return {
        "response_type": "update_template_card",
        "template_card": {
            "card_type": "button_interaction",
            "source": {"desc": "bkchat智能体", "desc_color": 0},
            "main_title": {
                "title": "欢迎使用bkchat智能体",
                "desc": f"{current_context.sender_id},您正在使用bkchat智能体！",
            },
            "sub_title_text": "请绑定一个智能体！",
            "button_selection": {
                "question_key": "bind_agent",
                "title": "智能体",
                "disable": False,
                "option_list": option_list,
                "selected_id": "agent_id",
            },
            "button_list": [
                {"text": "确认", "style": 4, "key": "bind_agent"},
                {"text": "上一页", "style": 4, "key": f"list_agent|{str(space_page - 1)}"},
                {"text": "下一页", "style": 4, "key": f"list_agent|{str(space_page + 1)}"},
            ],
            "task_id": get_return_task_id(current_context),
        },
    }


@register_plugin("bind_agent", [])
def bind_agent(current_context: WxWorkAiBotContext):
    bind_agent_id = current_context.message.wxaibot_template_card_event["selected_items"]["selected_item"][0][
        "option_ids"
    ]["option_id"][0]
    agent_info = BkAiDevApi().retrieve_agent(bind_agent_id)
    SessionAgentBinding.objects.update_or_create(
        sender=current_context.sender_code,
        group_id=current_context.group_id,
        defaults={
            "agent_code": bind_agent_id,
            "agent_name": agent_info["agent_name"],
            "group_type": current_context.from_type,
        },
    )
    return stream_msg(
        f"{current_context.sender_id},您已经绑定了智能体{agent_info['agent_name']}！",
        True,
        get_return_task_id(current_context),
    )
