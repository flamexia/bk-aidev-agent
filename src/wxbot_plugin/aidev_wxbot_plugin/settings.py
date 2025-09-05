"""
Django settings for aidev_wxbot_plugin.
"""

import os

BK_APIGW_MANAGER_URL_TMPL = os.getenv("BK_APIGW_MANAGER_URL_TMPL")
BKPAAS_BK_PLUGIN_APIGW_NAME = os.getenv("BKPAAS_BK_PLUGIN_APIGW_NAME", "bp-ai-bkchat-use")
BKPAAS_APP_SECRET = os.getenv("BKPAAS_APP_SECRET")
BKPAAS_APP_CODE = os.getenv("BKPAAS_APP_CODE")
BKPAAS_ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT")

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
    'aidev_wxbot_plugin.wxbot',
    'aidev_wxbot_plugin.wxaibot',
]

MIDDLEWARE = [
    'aidev_wxbot_plugin.utils.exception.ExceptionHandlerMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'aidev_wxbot_plugin.urls'

WSGI_APPLICATION = 'aidev_wxbot_plugin.wsgi.application'

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
