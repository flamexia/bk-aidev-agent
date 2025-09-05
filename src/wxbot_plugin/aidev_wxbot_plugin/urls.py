"""
Main URL routing for aidev_wxbot_plugin.
"""

from django.urls import include, path

urlpatterns = [path("", include("aidev_wxbot_plugin.wxaibot.urls"))]
