from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from .forms import UserSignUpForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Profile


def register(request: HttpRequest):
    if request.user.is_authenticated:
        logout(request)
    if request.method == "GET":
        return render(request, 'auth_app/register.html', {'form': UserSignUpForm(), 'title': 'Register user'})

    form = UserSignUpForm(request.POST, request.FILES)
    if form.is_valid():
        data = form.cleaned_data

        User.objects.create_user(username=data['username'], email=data['email'], password=data['password1'])
        
        Profile.objects.create(user=User.objects.get(username=data['username']), phone_number=data['phone_number'], address=data['address'], city=data['city'], state=data['state'], zip_code=data['zip_code'], profile_picture=data['profile_picture'])

        username = form.cleaned_data.get('username')
        messages.success(request, f'Account created for {username}!')
        return redirect('login')
    else:
        messages.warning(request, form.errors)
        return redirect('register')

@login_required
def profile(request):
    if request.method == "GET":
        return render(request, 'auth_app/profile.html', {'form': ProfileUpdateForm(instance=request.user.profile), 'user_form': UserUpdateForm(instance=request.user), 'title': 'Profile'})
    
    form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
    user_form = UserUpdateForm(request.POST, instance=request.user)
    if form.is_valid() and user_form.is_valid():
        form.save()
        user_form.save()
        messages.success(request, f'Account updated!')
        return redirect('profile')
    else:
        messages.warning(request, form.errors)
        return redirect('profile')

@login_required
def user_logout(request):
    logout(request)
    return render(request, 'auth_app/logout.html', {'title': 'Logout'})