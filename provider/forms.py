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
        """
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control col-md-7 col-xs-12',
            'required': 'required'
        })
        self.fields['address'].widget.attrs.update({
            'rows': 3,
            'class': 'form-control',
            'required': 'required'
        })
        self.fields['picture'].widget.attrs.update({
            'class': 'form-control',
            'style': 'border: 0px',
            'accept': 'image'
        })
        """
