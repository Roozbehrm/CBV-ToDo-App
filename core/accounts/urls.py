from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

app_name = "accounts"
urlpatterns = [
    path("api/v1/", include("accounts.api.v1.urls")),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("logout", LogoutView.as_view(next_page="/"), name="logout"),
]
