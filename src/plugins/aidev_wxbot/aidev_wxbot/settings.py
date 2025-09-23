#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Default settings for aidev_wxbot Django app.
These settings can be overridden in the main Django project's settings.
"""

import os

# aidev_wxbot app specific settings
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
IS_INDEPENDENT_BOT = os.getenv("IS_INDEPENDENT_BOT", "false").lower() == 'true'

# Default app configuration that can be added to main project settings
INSTALLED_APPS = [
    'rest_framework',
    'aidev_wxbot',
]


# Default logging configuration for aidev_wxbot
def get_aidev_wxbot_logging_config(log_dir=None):
    """
    Get logging configuration for aidev_wxbot app.

    Args:
        log_dir: Directory to store log files. If None, logs will only go to console.

    Returns:
        dict: Logging configuration dictionary
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'aidev_wxbot_standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            },
        },
        'handlers': {
            'aidev_wxbot_console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'aidev_wxbot_standard',
            },
        },
        'loggers': {
            'aidev_wxbot': {
                'handlers': ['aidev_wxbot_console'],
                'level': 'INFO',
                'propagate': False,
            },
            'pika': {
                'handlers': ['aidev_wxbot_console'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }

    # Add file handler if log_dir is provided
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        config['handlers']['aidev_wxbot_file'] = {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_dir, 'wxbot.log'),
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'formatter': 'aidev_wxbot_standard',
        }
        config['loggers']['aidev_wxbot']['handlers'].append('aidev_wxbot_file')
        config['loggers']['pika']['handlers'].append('aidev_wxbot_file')

    return config
