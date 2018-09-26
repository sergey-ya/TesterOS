from django import forms

from .models import Testing

class PassingTestCaseForm(forms.ModelForm):

    class Meta:
        model = Testing
        fields = ('os_name', 'os_version', 'os_release')