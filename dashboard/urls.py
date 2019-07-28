from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('event_handler', include('github_webhook_handler.urls'), name='event_handler'),
]
