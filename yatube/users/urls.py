from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        views.ChangePassword.as_view(),
        name='password_change',
    ),
    path(
        'password_change_done/',
        views.ChangePasswordDone.as_view(
            template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
]
