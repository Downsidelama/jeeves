from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

from .webhook_distributor import WebhookDistributor


@csrf_exempt
def index(request):
    webhook_distributor = WebhookDistributor(request)
    response = webhook_distributor.get_response()
    json_response = json.dumps(response, indent=4, sort_keys=True)
    return HttpResponse(json_response)
