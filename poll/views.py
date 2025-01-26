from django.shortcuts import render
from django.http import HttpResponse
from .models import Poll

def home(request):
    return render(request, 'poll/base.html')

def display_polls(request):
    return render(request, 'poll/display_polls.html', context={"polls": Poll.objects.all()})