from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.views.generic import UpdateView, CreateView

from dashboard.forms import PipeLineModelForm
from dashboard.models import PipeLine


@login_required
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context=context)


@login_required
def add_new_pipeline(request):
    return render(request, 'dashboard/pipeline_form.html')


class PipeLineCreateView(View):
    def get(self, request):
        form = PipeLineModelForm()
        context = {'form': form}
        return render(request, 'dashboard/pipeline_form.html', context)

    def post(self, request):
        form = PipeLineModelForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
        return render(request, 'dashboard/pipeline_form.html')


class PipeLineCreate(CreateView):
    model = PipeLine
    fields = ['name', 'description', 'script', 'repo_url']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PipeLineUpdate(UpdateView):
    model = PipeLine
    fields = ['name', 'description', 'script', 'repo_url']
