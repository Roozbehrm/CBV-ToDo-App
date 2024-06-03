# from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import RegisterForm
from django.urls import reverse, reverse_lazy

# Create your views here.


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    fields = "username", "password"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("todo:task_list")


class SignUpView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/signup.html"
