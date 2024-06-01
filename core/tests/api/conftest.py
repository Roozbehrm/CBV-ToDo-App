import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Profile
from todo.models import Task
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


User = get_user_model()

@pytest.fixture
def client():
    client = APIClient()
    return client

@pytest.fixture
def verified_user():
    user = User.objects.create_user(email='test@test.com', password='!@#12345', is_verified=True)
    return user


@pytest.fixture
def unverified_user():
    user = User.objects.create_user(email='test1@test.com', password='!@#12345')
    return user

@pytest.fixture
def token_auth_client(verified_user, client):
    url = reverse('accounts:api-v1:token_login')
    response =  client.post(url, data={'email':'test@test.com', 'password':'!@#12345'})
    client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
    return client

@pytest.fixture
def task(verified_user):
    profile = Profile.objects.get(user= verified_user )
    task = Task.objects.create(title= 'test', description= 'test', profile= profile)
    return task

@pytest.fixture
def jwt_token(verified_user, client):
    url = url = reverse('accounts:api-v1:jwt_create')
    response = client.post(url, data={'email':'test@test.com', 'password':'!@#12345'})
    return response.data

@pytest.fixture
def user_activation_token(verified_user, unverified_user):
    refresh = RefreshToken.for_user(unverified_user)
    return str(refresh.access_token)

@pytest.fixture
def user_reset_password_token(verified_user):
    uidb64 = urlsafe_base64_encode(force_bytes(verified_user.pk))
    token = PasswordResetTokenGenerator().make_token(verified_user)
    return {'token': token, 'uidb64': uidb64}