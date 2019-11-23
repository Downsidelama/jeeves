from django.urls import path
from .views import GithubPipeLineHandlerView, DashboardPipeLineHandlerView, PipeLineRestartView

app_name = 'pipelinehandler'
urlpatterns = [
    path('github-pipeline/', GithubPipeLineHandlerView.as_view(), name='github-handler'),
    path('dashboard-pipeline/<int:pk>/', DashboardPipeLineHandlerView.as_view(), name='dashboard-handler'),
    path('restart/<int:pk>', PipeLineRestartView.as_view(), name='restart'),
]
