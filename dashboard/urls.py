from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('event_handler', views.event_handler, name='event_handler'),
]
