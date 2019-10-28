from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views import View

from dashboard.forms import PipeLineModelForm, CustomUserCreationForm
from dashboard.models import PipeLine, PipeLineResult
from dashboard.pipeline_status import PipeLineStatus

import timeago


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        pipelines = PipeLine.objects.filter(user=request.user)
        context = {'pipelines': pipelines}
        return render(request, 'dashboard/index.html', context)


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'dashboard/registration.html', context={"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('dashboard:index'))


# TODO: Don't allow incorrect .yamls!
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


# TODO: Don't allow incorrect .yamls!
class PipeLineUpdateView(View, LoginRequiredMixin):
    def get(self, request, pk):
        model = get_object_or_404(PipeLine, pk=pk)
        if request.user != model.user:
            return redirect(reverse('dashboard:index'))
        form = PipeLineModelForm(instance=model)
        context = {'form': form, 'title': 'Edit {}'.format(model.name)}
        return render(request, 'dashboard/pipeline_form.html', context)

    def post(self, request, pk):
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
        running_pipelines = PipeLineResult \
                                .objects \
                                .filter(Q(pipeline=pk)
                                        & Q(status=PipeLineStatus.IN_PROGRESS.value)
                                        | Q(status=PipeLineStatus.IN_QUEUE.value)).order_by('pk') \
                                .reverse()[:5]

        for build in running_pipelines:
            build.elapsed_time = timeago.format(build.created_at, now())

        context = {
            'pipeline': pipeline,
            'running_pipelines': running_pipelines
        }
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


class PipeLineBuildsView(View, LoginRequiredMixin):
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        pipeline_builds = PipeLineResult.objects.filter(pipeline=pk)

        average_runtime = self._calculate_average_runtime(pipeline_builds)

        for build in pipeline_builds:
            build.status = PipeLineStatus(build.status).name
            build.created_at_hr = timeago.format(build.created_at, now())
            progress = 100

            if build.status not in [PipeLineStatus.IN_PROGRESS.name, PipeLineStatus.IN_QUEUE.value]:
                build.elapsed_time = timeago.format(build.build_start_time, build.build_end_time).replace(' ago', '')
            else:
                current_run_time = (now() - build.created_at).total_seconds()
                progress = int(current_run_time * 100 / average_runtime)
                if progress > 99:
                    progress = 99
                build.elapsed_time = timeago.format(build.created_at, now()).replace(' ago', '')
            build.progress = progress

        context = {
            "pipeline": pipeline,
            "pipeline_builds": pipeline_builds
        }

        return render(request, 'dashboard/pipeline_builds.html', context=context)

    def _calculate_average_runtime(self, pipeline_builds):
        all_time = 0
        filtered = pipeline_builds.filter(~Q(status=PipeLineStatus.IN_PROGRESS.value)
                                          & ~Q(status=PipeLineStatus.IN_QUEUE.value)
                                          & ~Q(build_end_time=None) & ~Q(build_start_time=None))
        # filtered = pipeline_builds.exclude(status=PipeLineStatus.IN_PROGRESS.value)
        if len(filtered) > 0:
            for build in filtered:
                all_time += (build.updated_at - build.created_at).total_seconds()
            results = all_time / len(filtered)
        else:
            results = 1
        print("avg: {}".format(results))
        return results
