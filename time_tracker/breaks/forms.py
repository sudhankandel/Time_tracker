from django import forms
from .models import Break

class BreakForm(forms.ModelForm):
    class Meta:
        model = Break
        fields = ['break_type', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.HiddenInput(),
            'end_time': forms.HiddenInput(),
        }