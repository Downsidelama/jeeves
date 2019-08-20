from django.urls import path, include
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('pipeline/add/', views.PipeLineCreateView.as_view(), name='new_pipeline'),
    path('pipeline/<int:pk>/', views.PipeLineUpdate.as_view(), name='view_pipeline'),
]
