import logging

import stackprinter
from rest_framework import status

logger = logging.getLogger("aidev_wxbot_plugin")


def handle_exception(exc):
    full_stack = stackprinter.format((exc.__class__, exc, exc.__traceback__))
    logger.error(msg=full_stack)


"""
自定义异常处理中间件
"""
import traceback
from logging import getLogger

from django.conf import settings
from django.http import JsonResponse

logger = getLogger(__name__)


class ExceptionHandlerMiddleware:
    """全局异常处理中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """处理视图中抛出的异常"""
        logger.error(f"视图异常: {str(exception)}", exc_info=True)

        # 判断是否是API请求（可以根据URL路径或请求头判断）
        error_data = {
            "result": False,
            "error": exception.__class__.__name__,
            "message": str(exception),
            "path": request.path,
            "method": request.method,
        }

        # 在调试模式下添加更多信息
        if settings.DEBUG:
            error_data.update({"debug": True, "traceback": traceback.format_exc()})
        full_stack = stackprinter.format((exception.__class__, exception, exception.__traceback__))
        logger.error(msg=full_stack)
        return JsonResponse(
            {"message": "系统出错，请联系管理员！", "result": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
