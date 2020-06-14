"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetCompleteView

app_name = 'myapp'

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_request, name="logout"),
    path('login/', views.login_request, name="login"),
    path('password_change/', PasswordChangeView.as_view(success_url='myapp/password_change/done/'),
         name="password_change"),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name="password_change_done"),
    path('password_reset/', PasswordResetView.as_view(success_url='done/'), name="password_reset"),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(success_url='/accounts/reset/done/'),
         name="password_reset_confirm"),
    path('reset/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),

]