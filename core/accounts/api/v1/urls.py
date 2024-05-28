from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'api-v1'

urlpatterns = [

    # password change
    path('change-password/', views.ChangePasswordApiView.as_view(), name='change_password'),

    # token auth
    path('registration/', views.RegistrationApiView.as_view(), name='registration'),
    path('token/login/', views.CustomObtainAuthToken.as_view(), name='token_login'),
    path('token/logout/', views.CustomDestroyToken.as_view(), name='token_logout'),

    #jwt auth
    path('jwt/create/', views.CustomTokenObtainPairView.as_view(), name='jwt_create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # getting profile
    path('profile/', views.ProfileApiView.as_view(), name='profile'),

    # activation
    path('activation/confirm/<str:token>', views.ActivationApiView.as_view(), name='activation'),
    path('activation/resend/', views.ActivationResendApiView.as_view(), name='activation_resend'),

    # password reset
    path('reset-password/', views.RequestPasswordResetApi.as_view(), name='request_reset_password'),
    path('reset-password/confirm/<uidb64>/<token>/', views.ResetPasswordConfirmApi.as_view(), name='confirm_reset_password',),
]