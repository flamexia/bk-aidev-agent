"""
URL routing for aidev_wxbot using DRF ViewSets.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WxAiBotViewSet

# 创建DRF路由器，设置trailing_slash=False避免末尾斜杠要求
router = DefaultRouter(trailing_slash=False)
router.register(r"", WxAiBotViewSet, basename="wxaibot")

urlpatterns = [
    # DRF ViewSet路由
    path("", include(router.urls)),
]
