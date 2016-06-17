from django.forms import ModelForm
from .models import Manager


class ManagerForm(ModelForm):
    class Meta:
        model = Manager
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ManagerForm, self).__init__(*args, **kwargs)
        self.fields['manager_code'].widget.attrs.update({
            'class': 'form-control',
            'required': 'required'
        })
