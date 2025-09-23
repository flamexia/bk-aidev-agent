#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL routing for aidev_wxbot Django app.

Include these URLs in your main project's urlpatterns:
    path('wxbot/', include('aidev_wxbot.urls')),
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aidev_wxbot.wxaibot.urls")),
]
