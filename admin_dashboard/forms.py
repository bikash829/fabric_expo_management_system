from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from phonenumber_field.formfields import SplitPhoneNumberField, PrefixChoiceField,PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from accounts.models import User




class StaffUserCreationForm(UserCreationForm):
    phone = SplitPhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            widgets=[
                # forms.Select(choices=PrefixChoiceField().choices),
                # forms.TextInput()
                forms.Select(attrs={'class': 'form-select w-25'},choices=PrefixChoiceField().choices),
                forms.TextInput(attrs={'class': 'form-control w-75'})
                ],
        )
    )
    additional_phone = SplitPhoneNumberField(
        required=False,
        widget=PhoneNumberPrefixWidget(
            widgets=[
                # forms.Select(choices=PrefixChoiceField().choices),
                # forms.TextInput()
                forms.Select(attrs={'class': 'form-select w-25'},choices=PrefixChoiceField().choices),
                forms.TextInput(attrs={'class': 'form-control w-75'})
                ],
        )
    )
    class Meta:
        model=get_user_model()
        fields = ['username','first_name','last_name','is_staff',
                  'is_active','is_superuser','email','password1','password2',
                  'gender','phone','additional_phone','date_of_birth','nationality']


class StaffChangeForm(UserChangeForm):
    phone = SplitPhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            widgets=[
                # forms.Select(choices=PrefixChoiceField().choices),
                # forms.TextInput()
                forms.Select(attrs={'class': 'form-select w-25'},choices=PrefixChoiceField().choices),
                forms.TextInput(attrs={'class': 'form-control w-75'})
                ],
        )
    )
    additional_phone = SplitPhoneNumberField(
        required=False,
        widget=PhoneNumberPrefixWidget(
            widgets=[
                # forms.Select(choices=PrefixChoiceField().choices),
                # forms.TextInput()
                forms.Select(attrs={'class': 'form-select w-25'},choices=PrefixChoiceField().choices),
                forms.TextInput(attrs={'class': 'form-control w-75'})
                ],
        )
    )
    class Meta:
        model=get_user_model()
        fields=['username','first_name','last_name','email','gender','phone','additional_phone','date_of_birth','nationality']
        exclude=['password1','password2']
        
    