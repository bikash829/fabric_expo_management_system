import datetime
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

""" functions """
def generate_upload_path(instance, filename, base_dir):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Generate a unique filename using UUID
    unique_filename = f'{uuid.uuid4()}.{ext}'
    # Get the current date
    current_date = datetime.now().strftime('%Y/%m/%d')
    # Construct the upload path
    
    return f'{base_dir}/{instance.username}/{current_date}/{unique_filename}'
    
def profile_photo_directory_path(instance, filename):
    return generate_upload_path(instance, filename, 'profile')


class User(AbstractUser):
    # gender 
    GENDER = [
        ('M','Male'),
        ('F','Female'),
        ('O', 'others')
    ]
    # verification status 
    IS_VERIFIED = [
            (1,"Verified"),
            (2,"Not Verified"),
            (3,"Pending")
        ]

    email=models.EmailField(unique=True)
    nationality = models.CharField(max_length=50,blank=True)
    gender = models.CharField(max_length=1,choices=GENDER)
    phone = PhoneNumberField()
    additional_phone = PhoneNumberField(blank=True)
    date_of_birth = models.DateField(null=True)
    profile_photo = models.ImageField(upload_to=profile_photo_directory_path,default="profile/avatar/blank-profile-picturepng.png") # f"{settings.MEDIA_URL}profile/avatar/blank-profile-picture.png"
    is_verified = models.IntegerField(choices=IS_VERIFIED,null=True)
    is_blocked= models.BooleanField(default=False)
    nationality = models.CharField(max_length=50)
    terms = models.BooleanField(default=0)

    @property
    def full_name(self):
        if self.first_name == '':
            return None
        else:
            return f"{self.first_name} {self.last_name}"
