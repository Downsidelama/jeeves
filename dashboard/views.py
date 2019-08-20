from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
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


class IndexView(View, LoginRequiredMixin):
    def get(self, request):
        pipelines = PipeLine.objects.filter(user=request.user)
        print(pipelines.count())
        context = {'pipelines': pipelines}
        return render(request, 'dashboard/index.html', context)


class PipeLineCreateView(View, LoginRequiredMixin):
    def get(self, request):
        form = PipeLineModelForm()
        context = {'form': form}
        return render(request, 'dashboard/pipeline_form.html', context)

    def post(self, request):
        form = PipeLineModelForm(request.POST or None)
        context = {'form': form}
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(obj.get_absolute_url())
        return render(request, 'dashboard/pipeline_form.html', context)


class PipeLineCreate(CreateView):
    model = PipeLine
    fields = ['name', 'description', 'script', 'repo_url']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PipeLineUpdate(UpdateView):
    model = PipeLine
    fields = ['name', 'description', 'script', 'repo_url']


class PipeLineDetailsView(View, LoginRequiredMixin):
    def get(self, request, pk):
        pipeline = PipeLine.objects.get(pk=pk)
        context = {
            'pipeline': pipeline
        }
        print(pipeline)
        return render(request, 'dashboard/pipeline_view.html', context)
