import traceback

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from dashboard.models import PipeLine
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class PipeLineModelForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))

    description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
    }))

    repo_url = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))

    script = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'novalidate': '',
    }), error_messages={'invalid_script': "The script is invalid!"})

    class Meta:
        model = PipeLine
        fields = ['name', 'description', 'repo_url', 'script']

        labels = {
            'repo_url': "Repository URL"
        }

    def is_valid(self):
        valid = super(PipeLineModelForm, self).is_valid()
        if not valid:
            return False

        try:
            PipeLineScriptParser().parse(script=self.data['script'])
        except (ValueError, AttributeError) as e:
            traceback.print_exc()
            self.add_error('script', str(e))
            return False
        return True


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = get_user_model()
        fields = ('username', 'email')
