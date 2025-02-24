from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_polls, name='display_polls'),
    path('create/', views.create_poll, name='create_poll'),
    path("my/", views.my_polls, name="my_polls")
]