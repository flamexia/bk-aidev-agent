# -*- coding: utf-8 -*-
from django.http import HttpResponse

"""
此文件为蓝鲸插件默认加载的url文件，其它各定义模块都从此处导入
1. 位置：bk_plugin_framework/services/bpf_service/urls.py
2. 前辍：/plugin_api/
"""
import requests
from blueapps.account.decorators import login_exempt
from django.conf import settings
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt


@login_exempt
@csrf_exempt
def to_wxbot_callback_path(request):
    query_string = request.META.get("QUERY_STRING", "")
    target_url = f"http://{settings.BK_APP_CODE}--wxbot.bkapp-{settings.BK_APP_CODE}-{settings.ENVIRONMENT}/callback"
    if query_string:
        target_url += f"?{query_string}"

    if request.method == "GET":
        response = requests.get(
            target_url,
            headers=dict(request.headers),
            data=request.body,
        )
    else:
        response = requests.post(
            target_url,
            headers=dict(request.headers),
            data=request.body,
        )
    return HttpResponse(
        response.content,
        status=response.status_code,
    )


urlpatterns = (path("", include("agent.urls")), re_path("^wxbot_callback$", to_wxbot_callback_path))
