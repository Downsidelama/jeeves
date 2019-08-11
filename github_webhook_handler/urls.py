from django.urls import path
from . import views

app_name = 'github_webhood_handler'
urlpatterns = [
    path('', views.index, name='index')
]
