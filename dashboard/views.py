from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from dashboard.forms import PipeLineModelForm
from dashboard.models import PipeLine


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        pipelines = PipeLine.objects.filter(user=request.user)
        context = {'pipelines': pipelines}
        return render(request, 'dashboard/index.html', context)


class PipeLineCreateView(View, LoginRequiredMixin):
    def get(self, request):
        form = PipeLineModelForm()
        context = {'form': form, 'title': 'Add new pipeline'}
        return render(request, 'dashboard/pipeline_form.html', context)

    def post(self, request):
        form = PipeLineModelForm(request.POST or None)
        context = {'form': form, 'title': 'Add new pipeline'}
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(obj.get_absolute_url())
        return render(request, 'dashboard/pipeline_form.html', context)


class PipeLineUpdateView(View, LoginRequiredMixin):
    def get(self, request, pk):
        model = get_object_or_404(PipeLine, pk=pk)
        form = PipeLineModelForm(instance=model)
        context = {'form': form, 'title': 'Edit {}'.format(model.name)}
        return render(request, 'dashboard/pipeline_form.html', context)

    def post(self, request, pk):
        print('post')
        model = get_object_or_404(PipeLine, pk=pk)
        form = PipeLineModelForm(request.POST or None, instance=model)
        if model.user == request.user:
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                return redirect(obj.get_absolute_url())
        else:
            return redirect(reverse('dashboard:index'))
        context = {'form': form, 'title': 'Edit {}'.format(model.name)}
        return render(request, 'dashboard/pipeline_form.html', context)


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
