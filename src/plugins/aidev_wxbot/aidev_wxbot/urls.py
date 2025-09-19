"""
Main URL routing for aidev_wxbot.
"""

from django.urls import include, path

urlpatterns = [path("", include("aidev_wxbot.wxaibot.urls"))]
