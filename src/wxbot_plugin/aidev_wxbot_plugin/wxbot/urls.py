"""
URL routing for aidev_wxbot_plugin.
"""

import os

from django.urls import path

from .views import CallBackView, DebugView

urlpatterns = [
    path("wxbot_callback", CallBackView.as_view(), name="wxbot_callback"),
]
if os.getenv("DEBUG") == "True":
    urlpatterns.append(path("debug", DebugView.as_view(), name="debug"))
