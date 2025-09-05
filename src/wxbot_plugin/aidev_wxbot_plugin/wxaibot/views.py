"""
Django implementation for aidev_wxbot_plugin.
"""

import json
import os
import threading
import time
import uuid
from logging import getLogger

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View

from aidev_wxbot_plugin.wxaibot.models import SessionAgentBinding

from .context import ContextGenerator, LlmChunkMsg, stream_msg
from .decryption import WXBizJsonMsgCrypt
from .plugins import ALL_PLUGIN
from ..utils.rabbitmq import rabbitmq_client

logger = getLogger(__name__)


class CallBackView(View):
    """对外提供服务的 Django 视图"""

    def __init__(self):
        super().__init__()
        self.S_TOKEN = os.getenv("S_TOKEN")
        self.S_ENCODING_AES_KEY = os.getenv("S_ENCODING_AES_KEY")
        self.WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")

    def _reply_wxaibot(self, payload: dict):
        msg_type = payload["msgtype"]
        if msg_type == "text":
            logger.info("go to reply_text")
            return_msg = self.reply_text(payload)
        elif msg_type == "event":
            logger.info("go to reply_event")
            return_msg = self.reply_event(payload)
        elif msg_type == "stream":
            logger.info("go to reply_stream")
            stream_id = payload["stream"]["id"]
            return_msg = self.reply_stream(stream_id)
        else:
            return_msg = {
                "msgtype": "stream",
                "stream": {
                    "id": f"stream_queue_{uuid.uuid4().hex}",
                    "finish": True,
                    "content": "您输入的内容我无法识别呢~",
                },
            }
        return return_msg

    @staticmethod
    def reply_stream(stream_id: str):
        try:
            # 从队列中取出单个元素
            llm_chunk = LlmChunkMsg(stream_id=stream_id)
            return_msg = llm_chunk.wxaibot_msg_json_from_cache(rabbitmq_client)
            return return_msg
        except Exception as e:
            logger.error(f"获取流式响应失败: {e}")
            return stream_msg("回答失败！", True, stream_id)

    def reply_event(self, payload: dict):
        current_context = ContextGenerator(payload).generate()
        return_msg = ALL_PLUGIN[current_context.message.event_key.split("|")[0]](current_context)
        return return_msg

    def reply_text(self, payload: dict):
        content = payload["text"]["content"]
        rtx_name = os.getenv("RTX_NAME")
        if content.startswith(f"@{rtx_name}"):
            content = content[len(f"@{rtx_name}") :].strip()

        current_context = ContextGenerator(payload).generate()
        if (
            not settings.IS_INDEPENDENT_BOT
            and not SessionAgentBinding.objects.filter(
                sender=current_context.sender_code, group_id=current_context.group_id
            ).exists()
        ):
            # 如果没有绑定过agent，强制要求绑定
            return_msg = ALL_PLUGIN["welcome"](current_context)
            return return_msg
        else:
            if settings.IS_INDEPENDENT_BOT:
                agent_apigw_name = settings.BKPAAS_BK_PLUGIN_APIGW_NAME
            else:
                agent_apigw_name = (
                    "bp"
                    + SessionAgentBinding.objects.get(
                        sender=current_context.sender_code, group_id=current_context.group_id
                    ).agent_code
                )
        if content.lower() in ALL_PLUGIN:
            # 如果是触发了固定的命令，就构建context，传递到命令处执行
            return_msg = ALL_PLUGIN[content](current_context)
            return return_msg
        else:
            # 生成流式响应ID
            stream_id = f"stream_queue_{int(time.time())}_{current_context.sender_code}"

            # 启动后台线程处理实际的AI请求
            thread = threading.Thread(
                target=self._process_ai_request_async, args=(content, stream_id, agent_apigw_name), daemon=True
            )
            thread.start()

            # 立即返回"正在思考中...."的消息
            return stream_msg("正在思考中....", False, stream_id)

    def _process_ai_request_async(self, content: str, stream_id: str, agent_apigw_name: str):
        """异步处理AI请求的后台方法"""
        try:
            start_time = time.time()
            first_response_time = None
            chat_root = (
                settings.BK_APIGW_MANAGER_URL_TMPL.format(api_name=agent_apigw_name)
                + "/"
                + "prod"
                + "/bk_plugin/plugin_api/chat_completion/"
            )
            logger.info(f"chat_root: {chat_root}")

            response = requests.post(
                chat_root,
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": {"chat_history": [{"role": "user", "content": content}]},
                    "chat_history": [{"role": "user", "content": content}],
                    "context": {"executor": "user"},
                    "execute_kwargs": {"stream": True},
                },
                stream=True,
            )

            docs = []
            buffer = ""  # 用于缓存不完整的数据
            llm_chunk = LlmChunkMsg(content="", is_finish=False, stream_id=stream_id)
            added_content = ""
            for chunk in response.iter_content(chunk_size=1024):  # 设置合适的chunk大小
                if chunk:
                    try:
                        chunk_str = chunk.decode("utf-8")
                        buffer += chunk_str
                        lines = buffer.split("\n")
                        buffer = lines[-1]

                        for line in lines[:-1]:
                            line = line.strip()
                            if not line:
                                continue
                            if line == "data: [DONE]":
                                continue
                            if line.startswith("data: "):
                                data_content = line[6:]
                                if not data_content:
                                    continue
                                chunk_json = json.loads(data_content)
                                if first_response_time is None:
                                    first_response_time = time.time()
                                    elapsed_time = first_response_time - start_time
                                    logger.info(f"从请求开始到第一次收到流式响应耗时: {elapsed_time:.3f} 秒")

                                event_type = chunk_json.get("event", "")
                                if event_type == "text":
                                    if chunk_json.get("content") == "正在思考...":
                                        continue
                                    added_content += chunk_json.get("content", "")
                                    if len(added_content) > 50:
                                        llm_chunk.content = llm_chunk.content + added_content
                                        llm_chunk.append_to_cache(rabbitmq_client)
                                        added_content = ""
                                elif event_type == "reference_doc":
                                    documents = chunk_json.get("documents", [])
                                    for doc_info in documents:
                                        if "metadata" in doc_info:
                                            docs.append(doc_info["metadata"])
                                    continue
                                elif event_type == "done":
                                    llm_chunk.docs = docs
                                    llm_chunk.is_finish = True
                                    llm_chunk.append_to_cache(rabbitmq_client)
                                else:
                                    logger.info(f"未知的事件类型: {event_type}")
                    except Exception as e:
                        logger.error(f"处理 chunk 时发生错误: {e}")
                        # 发生错误时，写入错误信息到流中
                        error_chunk = LlmChunkMsg(
                            content=f"处理请求时发生错误: {str(e)}", is_finish=True, stream_id=stream_id
                        )
                        error_chunk.append_to_cache(rabbitmq_client)
                        return

            # 处理缓冲区中剩余的数据
            if buffer.strip():
                line = buffer.strip()
                if line.startswith("data: ") and line != "data: [DONE]":
                    data_content = line[6:]
                    try:
                        chunk_json = json.loads(data_content)
                        event_type = chunk_json.get("event", "")
                        if event_type == "done":
                            llm_chunk.is_finish = True
                            llm_chunk.docs = docs
                            llm_chunk.append_to_cache(rabbitmq_client)
                    except Exception as e:
                        logger.info(f"缓冲区中的数据无法解析: {data_content}")
                        error_chunk = LlmChunkMsg(
                            content=f"解析响应数据时发生错误: {str(e)}", is_finish=True, stream_id=stream_id
                        )
                        error_chunk.append_to_cache(rabbitmq_client)

        except Exception as e:
            logger.error(f"异步处理AI请求失败: {e}")
            # 发生异常时，写入错误信息到流中
            error_chunk = LlmChunkMsg(content=f"请求处理失败: {str(e)}", is_finish=True, stream_id=stream_id)
            error_chunk.append_to_cache(rabbitmq_client)

    def get(self, request):
        """处理 GET 请求（验证 URL）"""
        crypt = WXBizJsonMsgCrypt(self.S_TOKEN, self.S_ENCODING_AES_KEY, "")
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
        crypt = WXBizJsonMsgCrypt(self.S_TOKEN, self.S_ENCODING_AES_KEY, "")
        msg_signature = request.GET.get("msg_signature")
        timestamp = request.GET.get("timestamp")
        nonce = request.GET.get("nonce")

        post_data = json.loads(request.body.decode("utf-8"))
        logger.info(f"请求消息回调 {post_data}, msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")
        ret, decrypt_post_json_data = crypt.DecryptMsg(post_data, msg_signature, timestamp, nonce)
        if ret != 0:
            logger.error("消息内容解密失败")
            return JsonResponse({"error": "解密失败"}, status=500)
        post_json = json.loads(decrypt_post_json_data)
        logger.info(f"企微发送的消息\n=============\n{post_json}")
        return_msg = self._reply_wxaibot(post_json)
        ret, wxbot_encrypt_msg = crypt.EncryptMsg(json.dumps(return_msg, ensure_ascii=False), nonce, timestamp)
        logger.info(f"返回的消息\n=============\n{return_msg}")
        return HttpResponse(content=wxbot_encrypt_msg, content_type="text/plain")


class DebugView(CallBackView):
    def post(self, request):
        return_msg = self._reply_wxaibot(json.loads(request.body.decode("utf-8")))
        return JsonResponse(return_msg)

    def get(self, request):
        return JsonResponse({"result": True})
