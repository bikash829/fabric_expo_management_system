from django.forms import ModelForm
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfilePhotoForm(ModelForm):
    class Meta:
        model = User
        fields = ['profile_photo']