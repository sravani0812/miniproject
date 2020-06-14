

import os
import re
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin
from django.core import mail
from django.shortcuts import render, redirect, resolve_url
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, FormView

from .models import Tutorial
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm, SetPasswordForm, UserModel,
                                       PasswordChangeForm, )
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from .forms import NewUserForm



def homepage(request):
   return render(request=request,
                  template_name="myapp/home.html",
                  context={"tutorials": Tutorial.objects.all})


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            return redirect("myapp:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request ,f"{msg}: {form.error_messages[msg]}")
    form = NewUserForm
    return render(request,
                  "myapp/register.html",
                  context={"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out Successfully!! ")
    return redirect("myapp:homepage")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('myapp:homepage')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    form = AuthenticationForm()
    return render(request,
                  "myapp/login.html",
                  {"form": form})
class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context
class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = 'myapp/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'myapp/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'myapp/password_reset_form.html'
    title = ('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class PasswordResetDoneView(PasswordContextMixin, TemplateView):
    template_name = 'myapp/password_reset_done.html'
    title = ('Password reset sent')


class PasswordResetCompleteView(PasswordContextMixin, TemplateView):
    template_name = 'myapp/password_reset_complete.html'
    title = ('Password reset complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context

class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'myapp/password_change_form.html'
    title = ('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = 'myapp/password_change_done.html'
    title = ('Password change successful')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
   

