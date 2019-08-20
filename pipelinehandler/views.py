from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class GithubPipeLineHandlerView(View):
    def get(self, request):
        return HttpResponse("OK")


class DashboardPipeLineHandlerView(View):
    def get(self, request):
        return HttpResponse("OK")
