from django.urls import path, include
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('pipeline/add/', views.add_new_pipeline, name='new_pipeline'),
]
