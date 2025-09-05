"""
Main URL routing for aidev_wxbot_plugin.
"""

import os

from django.urls import include, path

wxbot_type = os.getenv("WXBOT_TYPE", "wxbot")
if wxbot_type == "wxbot":
    urlpatterns = [
        path("", include("aidev_wxbot_plugin.wxbot.urls")),
    ]
elif wxbot_type == "wxaibot":
    urlpatterns = [path("", include("aidev_wxbot_plugin.wxaibot.urls"))]
