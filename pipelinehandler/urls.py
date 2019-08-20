from django.urls import path
from .views import GithubPipeLineHandlerView, DashboardPipeLineHandlerView

app_name = 'pipelinehandler'
urlpatterns = [
    path('github-pipeline/', GithubPipeLineHandlerView.as_view(), name='github-handler'),
    path('dashboard-pipeline/', DashboardPipeLineHandlerView.as_view(), name='dashboard-handler'),
]
