from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_polls, name='display_polls'),
    path('create/', views.create_poll, name='create_poll'),
    path('my/', views.my_polls, name='my_polls'),
    path('add_vote/', views.add_vote, name='vote'),
    path('my_votes/', views.my_votes, name="my_votes"),
    path('delete/', views.delete_poll, name="delete_poll")
]