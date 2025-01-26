from django.urls import path
from django.contrib.auth.views import (LoginView, PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name="auth_app/login.html"), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', PasswordResetView.as_view(template_name="auth_app/password_reset.html"), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name="auth_app/password_reset_done.html"), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name="auth_app/password_reset_confirm.html"), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name="auth_app/password_reset_complete.html"), name='password_reset_complete'),
]