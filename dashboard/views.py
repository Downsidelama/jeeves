from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context=context)
