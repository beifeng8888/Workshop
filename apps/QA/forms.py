from django import forms
from django.core.exceptions import ValidationError

from apps import QA


class QAForm(forms.ModelForm):
    class Meta:
        model = QA
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 100}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['answer'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance