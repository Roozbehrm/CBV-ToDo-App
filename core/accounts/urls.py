from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

app_name = 'accounts'
urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("logout", LogoutView.as_view(next_page='/'), name="logout"),
]