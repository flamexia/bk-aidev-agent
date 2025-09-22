"""
Django settings for aidev_wxbot.
"""

import os

BK_APIGW_MANAGER_URL_TMPL = os.getenv("BK_APIGW_MANAGER_URL_TMPL")
BKPAAS_BK_PLUGIN_APIGW_NAME = os.getenv("BKPAAS_BK_PLUGIN_APIGW_NAME", "")
BKPAAS_APP_SECRET = os.getenv("BKPAAS_APP_SECRET")
BKPAAS_APP_CODE = os.getenv("BKPAAS_APP_CODE")
BKPAAS_ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT")
WXAIBOT_TOKEN = os.getenv("BKAPP_WXAIBOT_TOKEN")
WXAIBOT_ENCODING_AES_KEY = os.getenv("BKAPP_WXAIBOT_ENCODING_AES_KEY")
WAXIBOT_NAME = os.getenv("BKAPP_WAXIBOT_NAME", "")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建日志目录
LOG_DIR = os.path.join(BASE_DIR, 'log')
os.makedirs(LOG_DIR, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('BKPAAS_APP_SECRET', 'dev')

DEBUG = False

ALLOWED_HOSTS = ['*']  # 允许所有主机访问，生产环境建议设置具体的域名

# Application definition
INSTALLED_APPS = [
    'rest_framework',
    'aidev_wxbot.wxaibot',
]

# Django REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],  # 禁用默认认证
    'DEFAULT_PERMISSION_CLASSES': [],  # 禁用默认权限检查
    'UNAUTHENTICATED_USER': None,  # 设置未认证用户为None
    'UNAUTHENTICATED_TOKEN': None,  # 设置未认证token为None
}

MIDDLEWARE = [
    'aidev_wxbot.utils.exception.ExceptionHandlerMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]
IS_INDEPENDENT_BOT = os.getenv("IS_INDEPENDENT_BOT", "false").lower() == 'true'

ROOT_URLCONF = 'aidev_wxbot.urls'

WSGI_APPLICATION = 'aidev_wxbot.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'wxbot.log'),
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'pika': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',  # 可以设置为 DEBUG, INFO, WARNING, ERROR, CRITICAL
            'propagate': False,
        },
    },
}
