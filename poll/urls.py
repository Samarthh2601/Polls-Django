from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('polls/', views.display_polls, name='display_polls'),
]