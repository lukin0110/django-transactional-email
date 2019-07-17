import json
from django import forms
from .models import TemplateVersion


class TemplateVersionForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, required=False)
    test_data = forms.CharField(widget=forms.Textarea, required=False)

    def clean_content(self):
        content = self.cleaned_data['content']
        return content

    def clean_test_data(self):
        test_data = self.cleaned_data['test_data']
        try:
            return json.loads(test_data)
        except json.decoder.JSONDecodeError:
            self.add_error('test_data', 'Invalid JSON')
        return test_data

    def save(self, version: TemplateVersion) -> TemplateVersion:
        data = self.cleaned_data
        version.content = data['content']
        version.test_data = data['test_data']
        version.save()
        return version
