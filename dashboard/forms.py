from django import forms

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
