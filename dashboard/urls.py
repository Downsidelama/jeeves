from django.urls import path, include
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('accounts/registration/', views.RegisterView.as_view(), name='registration'),

    path('pipeline/add/', views.PipeLineCreateView.as_view(), name='new_pipeline'),
    path('pipeline/<int:pk>/', views.PipeLineDetailsView.as_view(), name='view_pipeline'),
    path('pipeline/<int:pk>/delete/', views.PipeLineDeleteView.as_view(), name='delete_pipeline'),
    path('pipeline/<int:pk>/edit/', views.PipeLineUpdateView.as_view(), name='update_pipeline'),
    path('pipeline/<int:pk>/builds/', views.PipeLineBuildsView.as_view(), name='pipeline_builds'),
    path('livelog', views.livelog),
    path('livelog/<str:pk>/<int:current_size>', views.livelog_show),
]
