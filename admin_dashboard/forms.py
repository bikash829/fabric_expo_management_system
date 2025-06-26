from django.contrib.auth.models import Group, Permission
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from phonenumber_field.formfields import SplitPhoneNumberField, PrefixChoiceField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from admin_dashboard.utils import get_selected_permissions
from business_data.models import CompanyProfile




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
        
    
# manage user permissions 
class UserPermissionForm(forms.ModelForm):
    groups  = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        # queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"}),
    )
    user_permissions= forms.ModelMultipleChoiceField(
        # queryset=get_selected_permissions(),
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class":"form-control"}),
    )
    is_active = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    is_superuser = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = get_user_model()
        fields = ["groups", "user_permissions", "is_active", "is_superuser"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_permissions'].queryset = get_selected_permissions()


# class GroupForm(forms.ModelForm):
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,  # Use checkboxes instead of multi-select
#         required=False
#     )

#     class Meta:
#         model = Group
#         fields = ['name', 'permissions']

#     def __init__(self, *args, **kwargs):
#         super(GroupForm, self).__init__(*args, **kwargs)
#         if self.instance.pk:  # If editing an existing group
#             self.fields['permissions'].initial = self.instance.permissions.all()


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        # queryset=get_selected_permissions(),
        queryset=Permission.objects.none(),
        widget=forms.CheckboxSelectMultiple(), # Widget should be set here
        required=False
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'})
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = get_selected_permissions()
        
        
        
class CompanySelectForm(forms.ModelForm):
    company_name = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all(),
        empty_label="-- Select a Company --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Company"
    )

    class Meta:
        model = CompanyProfile
        fields = ['company_name']