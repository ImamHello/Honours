from django import forms
from .models import Postcode

class PostcodeForm(forms.ModelForm):
    class Meta:
        model = Postcode
        fields = ['postcode']
