from django import forms
from .models import Shift

# Form to clock in
class ClockInForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['clock_in_image']  # user uploads image on clock in


# Form to clock out
class ClockOutForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['clock_out_image']  # user uploads image on clock out