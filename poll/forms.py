from django import forms
from django.contrib.auth.models import User

from .models import Poll

class PollUpdateForm(forms.ModelForm):
    text = forms.CharField(max_length=512)
    active = forms.BooleanField()
    end_date = forms.DateTimeField()

    class Meta:
        model = Poll
        fields = ['text', 'active', 'end_date']