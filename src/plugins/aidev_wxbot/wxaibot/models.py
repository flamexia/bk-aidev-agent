from django.db import models
from django.utils import timezone


class SessionAgentBinding(models.Model):
    """会话代理绑定表"""

    GROUP_TYPE_CHOICES = [
        ("single", "私聊"),
        ("group", "群聊"),
    ]

    sender = models.CharField(max_length=200, verbose_name="发送者", db_index=True)
    group_id = models.CharField(max_length=200, verbose_name="群组ID，如果是私聊的话，群组id就是sender", db_index=True)
    group_type = models.CharField(max_length=200, choices=GROUP_TYPE_CHOICES, verbose_name="群组类型")
    space_id = models.CharField(max_length=200, verbose_name="空间ID", default="")
    space_name = models.CharField(max_length=200, verbose_name="空间名称", default="")
    space_name_en = models.CharField(max_length=200, verbose_name="空间名称英文", default="")
    agent_name = models.CharField(max_length=200, verbose_name="代理名称", default="")
    agent_code = models.CharField(max_length=200, verbose_name="代理code", db_index=True, default="")
    description = models.TextField(verbose_name="描述", default="")
    user_guide = models.TextField(verbose_name="用户指引", default="")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "session_agent_binding"
        verbose_name = "会话代理绑定"
        verbose_name_plural = "会话代理绑定"
        unique_together = ["group_id", "sender"]
