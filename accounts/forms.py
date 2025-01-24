
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import SplitPhoneNumberField, PrefixChoiceField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django import forms

User = get_user_model()

class ProfilePhotoForm(ModelForm):
    class Meta:
        model = User
        fields = ['profile_photo']

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    phone = SplitPhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            widgets=[
                forms.Select(choices=PrefixChoiceField().choices),
                forms.TextInput()
                # forms.Select(attrs={'class': 'form-select w-25'},choices=PrefixChoiceField().choices),
                # forms.TextInput(attrs={'class': 'form-control w-75'})
                ],
        )
    )
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['username','first_name','last_name','is_staff','is_superuser','email','password1','password2','gender','phone','additional_phone','date_of_birth','nationality']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'