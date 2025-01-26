from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(max_length=500)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    profile_picture = forms.ImageField(required=False)

class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(max_length=500)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'state', 'zip_code', 'profile_picture']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ['email']