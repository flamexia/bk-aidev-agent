"""
URL routing for aidev_wxbot.
"""

from django.urls import path

from .views import CallBackView

urlpatterns = [
    path("wxbot_callback", CallBackView.as_view(), name="wxbot_callback"),
]
