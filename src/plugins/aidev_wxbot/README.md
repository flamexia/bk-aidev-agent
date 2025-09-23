# aidev-wxbot

A Django app for WeChat AI bot integration with BK AI Dev platform.

## Installation

Install the package using pip:

```bash
pip install aidev-wxbot
```

## Quick Start

1. Add `aidev_wxbot` to your Django project's `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your other apps
    'rest_framework',
    'aidev_wxbot',
]
```

2. Add the required middleware to your `MIDDLEWARE` setting:

```python
MIDDLEWARE = [
    # ... your other middleware
    'aidev_wxbot.utils.exception.ExceptionHandlerMiddleware',
    # ... rest of your middleware
]
```

3. Include the aidev_wxbot URLs in your project's URL configuration:

```python
from django.urls import path, include

urlpatterns = [
    # ... your other URL patterns
    path('wxbot/', include('aidev_wxbot.urls')),
]
```

4. Configure the required environment variables:

```bash
# WeChat Bot Configuration
export BKAPP_WXAIBOT_TOKEN="your_wechat_bot_token"
export BKAPP_WXAIBOT_ENCODING_AES_KEY="your_encoding_aes_key"
export BKAPP_WAXIBOT_NAME="your_bot_name"

# BK Platform Configuration
export BKPAAS_APP_SECRET="your_app_secret"
export BKPAAS_APP_CODE="your_app_code"
export BKPAAS_ENVIRONMENT="your_environment"
export BK_APIGW_MANAGER_URL_TMPL="your_api_gateway_url"
export BKPAAS_BK_PLUGIN_APIGW_NAME="your_plugin_name"

# RabbitMQ Configuration (optional)
export RABBITMQ_HOST="localhost"
export RABBITMQ_PORT="5672"
export RABBITMQ_USER="guest"
export RABBITMQ_PASSWORD="guest"
export RABBITMQ_VHOST="/"

# Bot Mode (optional)
export IS_INDEPENDENT_BOT="false"
```

5. Run Django migrations (if any):

```bash
python manage.py migrate
```

## Configuration

### Logging

To configure logging for the aidev_wxbot app, you can use the provided logging configuration function:

```python
from aidev_wxbot.app_settings import get_aidev_wxbot_logging_config
import logging.config

# Configure logging with file output
log_dir = '/path/to/your/logs'
logging_config = get_aidev_wxbot_logging_config(log_dir)
logging.config.dictConfig(logging_config)

# Or configure logging with console output only
logging_config = get_aidev_wxbot_logging_config()
logging.config.dictConfig(logging_config)
```

### Django REST Framework

The app includes default DRF settings. You can override them in your main project settings:

```python
REST_FRAMEWORK = {
    # Your custom DRF settings
    # The app's default settings will be merged with these
}
```

## API Endpoints

Once installed and configured, the app provides the following endpoints:

- `POST /wxbot/` - WeChat bot webhook endpoint
- `GET /wxbot/` - WeChat bot verification endpoint

## Development

For development setup:

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Run tests: `pytest`

## License

MIT License