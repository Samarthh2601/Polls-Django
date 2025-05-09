from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_polls, name='display_polls'),
    path('create/', views.create_poll, name='create_poll'),
    path('my/', views.my_polls, name='my_polls'),
    path('add_vote/', views.add_vote, name='vote'),
    path('my_votes/', views.my_votes, name="my_votes"),
    path('delete/', views.delete_poll, name="delete_poll"),
    path('edit/', views.edit_poll, name="edit_poll"),
    path('expired/', views.display_expired_polls, name="expired_polls"),
    path('view/', views.view_poll, name="view_poll"),
    path('search/', views.search, name="search"),
]
