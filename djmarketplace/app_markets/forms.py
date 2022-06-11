from django import forms
from django.utils.translation import gettext_lazy as _


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(label=_('quantity'), min_value=0)

class DatePeriodForm(forms.Form):
    start_period = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_period = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))