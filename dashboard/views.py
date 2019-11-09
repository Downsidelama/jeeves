import json
import os
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from dashboard.forms import PipeLineModelForm, CustomUserCreationForm
from dashboard.models import PipeLine, PipeLineResult
from dashboard.pipeline_status import PipeLineStatus

import timeago

from jeeves import settings

chars_to_filter = ['[0K', '[?25l ', '[K', '[?25h', '', '[?25l']


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
            return redirect("{}?successful_registration".format(reverse('login')))
        else:
            return render(request, 'dashboard/registration.html', context={"form": form})


# TODO: Don't allow incorrect .yamls!
class PipeLineCreateView(View, LoginRequiredMixin):
    def get(self, request):
        form = PipeLineModelForm()
        context = {'form': form, 'title': 'Add new pipeline'}
        return render(request, 'dashboard/pipeline/pipeline_form.html', context)

    def post(self, request):
        form = PipeLineModelForm(request.POST or None)
        context = {'form': form, 'title': 'Add new pipeline'}
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(obj.get_absolute_url())
        return render(request, 'dashboard/pipeline/pipeline_form.html', context)


# TODO: Don't allow incorrect .yamls!
class PipeLineUpdateView(View, LoginRequiredMixin):
    def get(self, request, pk):
        model = get_object_or_404(PipeLine, pk=pk)
        if request.user != model.user:
            return redirect(reverse('dashboard:index'))
        form = PipeLineModelForm(instance=model)
        context = {'form': form, 'title': 'Edit {}'.format(model.name)}
        return render(request, 'dashboard/pipeline/pipeline_form.html', context)

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
        return render(request, 'dashboard/pipeline/pipeline_form.html', context)


class PipeLineDetailsView(View, LoginRequiredMixin):
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        if pipeline.is_github_pipeline:
            return redirect(reverse('dashboard:pipeline_builds', kwargs={'pk': pipeline.pk}))
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
        return render(request, 'dashboard/pipeline/pipeline_view.html', context)


class PipeLineDeleteView(View, LoginRequiredMixin):
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk, user=request.user)
        if pipeline:
            context = {'pipeline': pipeline}
            return render(request, 'dashboard/pipeline/pipeline_delete.html', context=context)
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
            if build.status not in [PipeLineStatus.IN_PROGRESS.name, PipeLineStatus.IN_QUEUE.name]:
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

        return render(request, 'dashboard/pipeline/pipeline_builds.html', context=context)

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
        return results


class PipeLineBuildDetailsView(View):
    def get(self, request, pk, id):
        pipeline, pipeline_result = self.get_pipeline_details(id, pk)
        context = {
            'pipeline': pipeline,
            'pipeline_result': pipeline_result
        }
        return render(request, 'dashboard/pipeline/pipeline_build_details.html', context=context)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk, id):
        """Getting some status data"""
        pipeline, pipeline_result = self.get_pipeline_details(id, pk)

        context = {
            'query_next': pipeline_result.status not in [PipeLineStatus.SUCCESS.value,
                                                         PipeLineStatus.FAILED.value],
            'status': pipeline_result.status,
            'runtime': pipeline_result.elapsed_time,
            'created_at_hr': pipeline_result.created_at_hr,
        }
        return HttpResponse(json.dumps(context))

    def get_pipeline_details(self, id, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        pipeline_result = get_object_or_404(PipeLineResult, pk=id)
        if pipeline_result.pipeline.pk != pipeline.pk:
            raise Http404
        pipeline_result.created_at_hr = timeago.format(pipeline_result.created_at, now())
        if pipeline_result.status not in [PipeLineStatus.IN_PROGRESS.value, PipeLineStatus.IN_QUEUE.value]:
            pipeline_result.elapsed_time = timeago.format(pipeline_result.build_start_time,
                                                          pipeline_result.build_end_time).replace(' ago', '')
        else:
            pipeline_result.elapsed_time = timeago.format(pipeline_result.created_at, now()).replace(' ago', '')
        return pipeline, pipeline_result


class LiveLog(View):
    def get(self, request, pk, id, current_size):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        pipeline_result = get_object_or_404(PipeLineResult, pk=id)
        if pipeline_result.pipeline.pk != pipeline.pk:
            raise Http404
        try:
            with open(os.path.join(settings.BASE_DIR, f'logs/{pipeline_result.log_file_name}.log'), 'rb') as f:
                f.seek(current_size)
                t = f.read().decode()
                t = re.sub(r'\x1b\[[?]?[0-9;]*[mKhl]', '', t, flags=re.IGNORECASE)
                for chars in chars_to_filter:
                    t = t.replace(chars, '')
                current_size = f.tell()
                dumps = json.dumps({"text": f"{t}", "current_size": current_size,
                                    "query_next": pipeline_result.status not in [PipeLineStatus.SUCCESS.value,
                                                                                 PipeLineStatus.FAILED.value]})
                return HttpResponse(dumps)
        except:
            return HttpResponse('{"text": "", "current_size": 0, "query_next": true}', content_type='application/json')
