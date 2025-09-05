"""
Django implementation for aidev_wxbot_plugin.
"""

import json
import os
import xml.etree.cElementTree as ET
from logging import getLogger

from django.http import HttpResponse, JsonResponse
from django.views import View

from .context import ContextGenerator, WxWorkBotContext
from .decryption import WXBizMsgCrypt
from ..api.bkaidev import AgentBackend
from ..api.wxbot import WxbotApi
from ..context import Context
from ..context.message import MarkdownMessage, Message, MessageTarget, WxBotSurfaceMessage
from ..utils import element_to_dict
from ..utils.exception import handle_exception

logger = getLogger(__name__)


class CallBackView(View):
    """对外提供服务的 Django 视图"""

    def __init__(self):
        super().__init__()
        self.S_TOKEN = os.getenv("S_TOKEN")
        self.S_ENCODING_AES_KEY = os.getenv("S_ENCODING_AES_KEY")
        self.WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")

    def get(self, request):
        """处理 GET 请求（验证 URL）"""
        crypt = WXBizMsgCrypt(self.S_TOKEN, self.S_ENCODING_AES_KEY, "")
        msg_signature = request.GET.get("msg_signature")
        timestamp = request.GET.get("timestamp")
        nonce = request.GET.get("nonce")
        echostr = request.GET.get("echostr")

        logger.info("验证 URL")
        ret, echostr = crypt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        logger.info(echostr)
        if ret != 0:
            logger.error("URL 验证失败")
            return JsonResponse({"error": "验证失败"}, status=500)
        return HttpResponse(echostr)

    def post(self, request):
        """处理 POST 请求（消息回调）"""
        crypt = WXBizMsgCrypt(self.S_TOKEN, self.S_ENCODING_AES_KEY, "")
        msg_signature = request.GET.get("msg_signature")
        timestamp = request.GET.get("timestamp")
        nonce = request.GET.get("nonce")

        logger.info("请求消息回调")
        post_data = request.body.decode("utf-8")
        ret, decrypt_post_data = crypt.DecryptMsg(post_data, msg_signature, timestamp, nonce)
        if ret != 0:
            logger.error("消息内容解密失败")
            return JsonResponse({"error": "解密失败"}, status=500)

        xml_tree = ET.fromstring(decrypt_post_data)
        payload = element_to_dict(xml_tree)
        ctx = self.generate_ctx(payload)
        if ctx is None:
            return JsonResponse({"result": True})
        self.get_res_from_bkaidev(ctx)
        return JsonResponse({"result": True})

    def get_res_from_bkaidev(self, ctx: WxWorkBotContext):
        if ctx.message.msg_type == "event":
            return
        res = AgentBackend().invoke(ctx.message.text)
        answer = "模型暂无输出！"
        if res.get("outputs"):
            answer = res.get("outputs")
        return self._send_msg(
            MarkdownMessage(answer, target=MessageTarget(target_type=ctx.from_type, target_id=ctx.group_id))
        )

    def generate_ctx(self, payload) -> Context:
        ctx_generator = ContextGenerator(payload=payload)
        context = ctx_generator.generate()
        return context

    def send_msg(self, request):
        """处理发送消息的请求"""
        payload = request.POST if request.method == "POST" else request.GET
        message = Message()
        message.wxbot_send_body = payload
        try:
            if "@" in payload.get("chatid", "") or not payload.get("chatid", ""):
                raise Exception("chat id 不可以为空或者带有 @")
            if "@all" in payload.get("mentioned_list", ""):
                raise Exception("不可以 @all!")
            res = WxbotApi().send(payload, self.WEBHOOK_KEY)
            return JsonResponse(res)
        except Exception as e:
            handle_exception(e)
            return JsonResponse({"result": False, "exception": str(e)})

    def _send_msg(self, message):
        logger.info(f"send_msg: {message}")
        if "@" in message.target.target_id or not message.target.target_id:
            raise Exception("chat id 不可以为空或者带有 @")
        if message.mention_list and "@all" in message.mention_list:
            raise Exception("不可以 @all!")
        return getattr(self, f"_send_{message.msg_type}")(message)

    def _send_to_wxbot(self, message, payload):
        if message.mention_list:
            payload["text"]["mentioned_list"] = message.mention_list
        if message.target.visible_user:
            payload["visible_to_user"] = message.target.visible_user
        try:
            if message.response_code:
                payload["response_type"] = "replace_origin"
                WxbotApi().replace_origin(payload, message.response_code)
            else:
                WxbotApi().send(payload, self.WEBHOOK_KEY)
            return JsonResponse({"result": True})
        except Exception as e:
            handle_exception(e)
            return JsonResponse({"result": False, "exception": str(e)})

    def _send_markdown(self, message: Message):
        payload = {
            "chatid": message.target.target_id,
            "msgtype": "markdown",
            "markdown": {
                "content": message.text,
                "at_short_name": True,
                "attachments": message.wx_markdown_attachments,
            },
        }
        return self._send_to_wxbot(message, payload)

    def _send_text(self, message: Message):
        payload = {
            "chatid": message.target.target_id,
            "msgtype": "text",
            "text": {"content": message.text, "mentioned_mobile_list": []},
        }
        return self._send_to_wxbot(message, payload)

    def _send_wxbot_surface(self, message: WxBotSurfaceMessage):
        payload = {"chatid": message.target.target_id}
        payload.update(message.wx_json)
        return self._send_to_wxbot(message, payload)


class DebugView(CallBackView):
    def post(self, request):
        ctx = self.generate_ctx(json.loads(request.body.decode("utf-8")))
        if ctx is None:
            return JsonResponse({"result": True})
        self.get_res_from_bkaidev(ctx)
        return JsonResponse({"result": True})

    def get(self, request):
        return JsonResponse({"result": True})
