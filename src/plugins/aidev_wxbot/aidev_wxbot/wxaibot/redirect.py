import requests
from blueapps.account.decorators import login_exempt
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@login_exempt
@csrf_exempt
def to_wxbot_callback_path(request):
    query_string = request.META.get("QUERY_STRING", "")
    target_url = f"http://{settings.BK_APP_CODE}--wxbot.bkapp-{settings.BK_APP_CODE}-{settings.ENVIRONMENT}/callback/?{query_string}"
    if request.method == "GET":
        response = requests.get(
            target_url,
            headers=dict(request.headers),
            data=request.body,
        )
    else:
        response = requests.post(
            target_url,
            headers=dict(request.headers),
            data=request.body,
        )
    return HttpResponse(
        response.content,
        status=response.status_code,
    )
