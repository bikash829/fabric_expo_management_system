
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import SplitPhoneNumberField, PrefixChoiceField,PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()

""" Update profile photo form """
class ProfilePhotoForm(ModelForm):
    class Meta:
        model = User
        fields = ['profile_photo']


""" User creation form"""
class CustomUserCreationForm(UserCreationForm):
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
        model = User
        fields = '__all__'
        # fields = ['username','first_name','last_name','is_staff','is_superuser','email','password1','password2','gender','phone','additional_phone','date_of_birth','nationality']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


""" Update user info form """
class CustomUserChangeForm(UserChangeForm):
    template_name = "accounts/form_template/user_form.html"
    password = None
    phone = SplitPhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            widgets=[
                forms.Select(attrs={'class': 'form-select w-25'}, choices=PrefixChoiceField().choices),
                forms.TextInput(attrs={'class': 'form-control w-75'})
            ],
        )
    )
    additional_phone = SplitPhoneNumberField(
        required=False,
        widget=PhoneNumberPrefixWidget(
            widgets=[
                forms.Select(attrs={'class': 'form-select w-25'}, choices=PrefixChoiceField().choices),
                forms.TextInput(attrs={'class': 'form-control w-75'})
            ],
        )
    )

    class Meta:
        model = get_user_model()
        fields = [ 'first_name', 'last_name', 'gender', 'date_of_birth', 'phone', 'additional_phone', 'nationality']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
        }


""" Email update form """
class UserEmailUpdateForm(forms.ModelForm):
    # "Extends User model form to include password verification"
    password = forms.CharField(
        label="Current Password", 
        widget=forms.PasswordInput(), 
        required=True
    )

    class Meta:
        model = User
        fields = ["email"]

    # initiate logged in user
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

    # check the password is correct
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user or not check_password(password, self.user.password):
            raise forms.ValidationError("Incorrect password.")
        return password
    
    # check if the email is same or already registered 
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email == self.user.email:
            raise forms.ValidationError("The new email address cannot be the same as the current email address.")
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    

""" username change form """
class ChangeUsernameForm(forms.ModelForm):
    pass 