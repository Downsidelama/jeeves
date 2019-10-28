from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from dashboard.models import PipeLine


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
    }))

    class Meta:
        model = PipeLine
        fields = ['name', 'description', 'repo_url', 'script']

        labels = {
            'repo_url': "Repository URL"
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = get_user_model()
        fields = ('username', 'email')
