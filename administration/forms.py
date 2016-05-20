from django.forms import ModelForm
from .models import Admin, Problem, ProblemCategory, Toilet, UserProfile
from reporting.models import Ticket
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class AdminForm(ModelForm):
    class Meta:
        model = Admin
        fields = '__all__'


class ProblemCategoryForm(ModelForm):
    class Meta:
        model = ProblemCategory
        fields = '__all__'


class ProblemForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('submit', 'Add Problem'))

    class Meta:
        model = Problem
        fields = '__all__'


class ToiletForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ToiletForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('submit', 'Add Toilet'))

    class Meta:
        model = Toilet
        fields = '__all__'


class TicketForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('submit', 'Add Ticket'))

    class Meta:
        model = Ticket
        fields = '__all__'


class UserForm(ModelForm):
    class Meta:
        model = Toilet
        fields = '__all__'


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
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
