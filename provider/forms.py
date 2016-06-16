from django.forms import ModelForm
from .models import Provider


class ProviderForm(ModelForm):
    class Meta:
        model = Provider
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.fields['manager'].widget.attrs.update({
            'class': 'form-control',
            'required': 'required'
        })
        self.fields['toilets'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['problems'].widget.attrs.update({
            'class': 'form-control',
            'required': 'required'
        })
        self.fields['description'].widget.attrs.update({
            'rows': 3,
            'class': 'form-control',
        })
