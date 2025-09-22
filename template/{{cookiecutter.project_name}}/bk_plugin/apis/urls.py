# -*- coding: utf-8 -*-

"""
此文件为蓝鲸插件默认加载的url文件，其它各定义模块都从此处导入
1. 位置：bk_plugin_framework/services/bpf_service/urls.py
2. 前辍：/plugin_api/
"""

from aidev_wxbot.wxaibot.redirect import to_wxbot_callback_path
from django.urls import include, path, re_path

urlpatterns = (
    path("", include("agent.urls")),
    re_path(r"^wxbot_callback/?$", to_wxbot_callback_path),
)
