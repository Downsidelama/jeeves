from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context=context)


@login_required
def add_new_pipeline(request):
    return render(request, 'dashboard/add_new_pipeline.html')
