import json
import math
import os
import re

from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
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

# Console characters to filter out, might be obsolete without the -t parameter in docker run.
chars_to_filter = ['[0K', '[?25l ', '[K', '[?25h', '', '[?25l']


class IndexView(LoginRequiredMixin, View):
    """Front page view"""
    def get(self, request):
        pipelines = PipeLine.objects.filter(user=request.user)
        context = {'pipelines': pipelines}
        return render(request, 'dashboard/index.html', context)


class RegisterView(View):
    """Registration handling view"""
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


class PipeLineCreateView(View, LoginRequiredMixin):
    """View to create pipelines"""
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


class PipeLineUpdateView(View, LoginRequiredMixin):
    """View to update pipelines (uses the same template as create view)"""
    def get(self, request, pk):
        model = get_object_or_404(PipeLine, pk=pk)
        if request.user.pk != model.user.pk:
            return redirect(reverse('dashboard:index'))
        form = PipeLineModelForm(instance=model)
        context = {'form': form, 'title': 'Edit {}'.format(model.name)}
        return render(request, 'dashboard/pipeline/pipeline_form.html', context)

    def post(self, request, pk):
        model = get_object_or_404(PipeLine, pk=pk)
        form = PipeLineModelForm(request.POST or None, instance=model)
        if model.user.pk == request.user.pk:
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                return redirect(obj.get_absolute_url())
        else:
            return redirect(reverse('dashboard:index'))
        context = {'form': form, 'title': 'Edit {}'.format(model.name)}
        return render(request, 'dashboard/pipeline/pipeline_form.html', context)


class PipeLineDetailsView(View, LoginRequiredMixin):
    """View to list the details of individual pipelines."""
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        if pipeline.user.pk == request.user.pk:
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
        else:
            return redirect(reverse('login'))


@method_decorator(login_required, name='dispatch')
class PipeLineDeleteView(View, LoginRequiredMixin):
    """View to delete pipelines."""
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk, user=request.user)
        if pipeline.user.pk == request.user.pk:
            if pipeline:
                context = {'pipeline': pipeline}
                return render(request, 'dashboard/pipeline/pipeline_delete.html', context=context)
            else:
                return redirect(reverse('dashboard:index'))
        else:
            return redirect(reverse('login'))

    def post(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk, user=request.user)
        if pipeline.user.pk == request.user.pk:
            if pipeline:
                pipeline.delete()
            return redirect(reverse('dashboard:index'))
        else:
            return redirect(reverse('login'))


def redirect_to_page_one(request, pk):
    """Compatibility with older code"""
    return redirect(reverse('dashboard:pipeline_builds', kwargs={'pk': pk, 'page': 1}))


@method_decorator(login_required, name='dispatch')
class PipeLineBuildsView(View, LoginRequiredMixin):
    """List of the pipelines for the project."""
    item_per_page = 25

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Allow AJAX requests without CSRF protection
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk, page):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        if pipeline.user.pk == request.user.pk:
            pipeline_builds = self._get_builds(pk, page)
            if not pipeline_builds:
                return HttpResponse('{"error": "Invalid parameters"}', content_type="application/json")
            average_runtime = self._calculate_average_runtime(pk)
            self.set_custom_attributes_in_builds(average_runtime, pipeline_builds)

            pipeline_builds_json = []
            for pipeline_build in pipeline_builds:
                data = {
                    'pk': pipeline_build.pk,
                    'progress': pipeline_build.progress,
                    'status': pipeline_build.status,
                    'elapsed_time': pipeline_build.elapsed_time,
                    'created_at_hr': pipeline_build.created_at_hr,
                }
                pipeline_builds_json.append(data)

            return HttpResponse(json.dumps(pipeline_builds_json), content_type="application/json")
        else:
            return HttpResponse('{"error": "Invalid parameters"}', content_type="application/json")

    def get(self, request, pk, page=1):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        if pipeline.user.pk == request.user.pk:
            pipeline_builds = self._get_builds(pk, page)
            if pipeline_builds is None:
                return redirect(reverse('dashboard:pipeline_builds', kwargs={'pk': pk, 'page': 1}))
            all_page, buttons = self._create_pagination(page, pk)
            average_runtime = self._calculate_average_runtime(pk)
            self.set_custom_attributes_in_builds(average_runtime, pipeline_builds)

            context = {
                "pipeline": pipeline,
                "pipeline_builds": pipeline_builds,
                "pagination_buttons": buttons,
                "last_page": all_page,
            }

            return render(request, 'dashboard/pipeline/pipeline_builds.html', context=context)
        else:
            return redirect(reverse('login'))

    def set_custom_attributes_in_builds(self, average_runtime, pipeline_builds):
        """Calculate values that needs to be displayed based on information stored in the DB."""
        for build in pipeline_builds:
            build.status = PipeLineStatus(build.status).name
            build.created_at_hr = timeago.format(build.created_at, now())
            progress = 100
            if build.status not in [PipeLineStatus.IN_PROGRESS.name, PipeLineStatus.IN_QUEUE.name]:
                build.elapsed_time = timeago.format(build.build_start_time, build.build_end_time).replace(' ago',
                                                                                                          '')
            else:
                current_run_time = (now() - build.created_at).total_seconds()
                progress = int(current_run_time * 100 / average_runtime)
                if progress > 99:
                    progress = 99
                build.elapsed_time = timeago.format(build.created_at, now()).replace(' ago', '')
            build.progress = progress
            build.status = build.status.title().replace('_', ' ')

    def _get_builds(self, pk, page):
        """Gets the builds on page :page"""
        if page == 1:
            return PipeLineResult.objects.filter(pipeline=pk).order_by('-pk')[:self.item_per_page]
        elif page < 1:
            return None
        else:
            pipeline_builds = PipeLineResult.objects.filter(pipeline=pk).order_by('-pk')[
                              self.item_per_page * (page - 1): self.item_per_page * page]
            return pipeline_builds

    def _create_pagination(self, page, pk):
        """Returns the pagination list"""
        all_page = math.ceil(PipeLineResult.objects.filter(pipeline=pk).count() / self.item_per_page)
        if all_page == 0:
            all_page = 1
        buttons = []
        button_count = 0
        for i in range(page - 3, page):
            if i > 0:
                buttons.append(i)
                button_count += 1
        remaining = (3 - button_count)
        for i in range(page, min(page + 4 + remaining, all_page + 1)):
            buttons.append(i)
            button_count += 1
        return all_page, buttons

    def _calculate_average_runtime(self, pk):
        """Calculates the average runtime based on finished pipeline results."""
        all_time = 0
        pipeline_builds = PipeLineResult.objects.filter(pipeline=pk)
        filtered = pipeline_builds.filter(~Q(status=PipeLineStatus.IN_PROGRESS.value)
                                          & ~Q(status=PipeLineStatus.IN_QUEUE.value)
                                          & ~Q(build_end_time=None) & ~Q(build_start_time=None)) \
            .exclude(status=PipeLineStatus.IN_PROGRESS.value)
        if len(filtered) > 0:
            for build in filtered:
                all_time += (build.updated_at - build.created_at).total_seconds()
            results = all_time / len(filtered)
        else:
            results = 1
        return results


class PipeLineBuildDetailsView(View):
    """Displays a detailed pipeline build page."""
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
    """View for AJAX requests"""
    def get(self, request, pk, id, current_size):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        pipeline_result = get_object_or_404(PipeLineResult, pk=id)
        if pipeline_result.pipeline.pk != pipeline.pk:
            raise Http404
        try:
            with open(os.path.join(settings.BASE_DIR, f'logs/{pipeline_result.log_file_name}.log'), 'rb') as f:
                f.seek(current_size)
                t = f.read().decode()
                #t = re.sub(r'\x1b\[[?]?[0-9;]*[mKhl]', '', t, flags=re.IGNORECASE)
                #for chars in chars_to_filter:
                #    t = t.replace(chars, '')
                current_size = f.tell()
                dumps = json.dumps({"text": f"{t}", "current_size": current_size,
                                    "query_next": pipeline_result.status not in [PipeLineStatus.SUCCESS.value,
                                                                                 PipeLineStatus.FAILED.value]})
                return HttpResponse(dumps)
        except:
            return HttpResponse('{"text": "", "current_size": 0, "query_next": true}', content_type='application/json')


@method_decorator(login_required, name='dispatch')
class ProfileView(View, LoginRequiredMixin):
    """View for modifying profile information"""
    def get(self, request):
        password_change = PasswordChangeForm(request.user)
        return render(request, 'dashboard/profile/index.html', context={'form': password_change})

    def post(self, request):
        if {'last_name', 'first_name', 'email'} <= set(request.POST):
            user = get_user_model().objects.get(pk=request.user.pk)
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()

        if {'new_password1', 'new_password2', 'old_password'} <= set(request.POST):
            user = get_user_model().objects.get(pk=request.user.pk)
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
            else:
                return render(request, 'dashboard/profile/index.html', context={'form': password_form})

        return redirect('dashboard:profile')
