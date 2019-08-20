from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        pipelines = PipeLine.objects.filter(user=request.user)
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
        pipeline = get_object_or_404(PipeLine, pk=pk)
        context = {
            'pipeline': pipeline
        }
        print(pipeline)
        return render(request, 'dashboard/pipeline_view.html', context)


class PipeLineDeleteView(View, LoginRequiredMixin):
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk, user=request.user)
        if pipeline:
            context = {'pipeline': pipeline}
            return render(request, 'dashboard/pipeline_delete.html', context=context)
        else:
            return redirect(reverse('dashboard:index'))

    def post(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk, user=request.user)
        if pipeline:
            pipeline.delete()
        return redirect(reverse('dashboard:index'))
