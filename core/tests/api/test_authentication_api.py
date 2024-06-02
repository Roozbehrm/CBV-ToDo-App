import pytest
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile


User = get_user_model()


@pytest.mark.django_db
class TestTaskApi:
    def test_regiteration(self, client):
        url = reverse("accounts:api-v1:registration")
        response = client.post(
            url,
            data={
                "email": "test1@test1.com",
                "password": "!@#12345",
                "password1": "!@#12345",
            },
        )
        assert response.status_code == 201
        assert response.data["email"] == "test1@test1.com"

    def test_token_login(self, client, verified_user):
        url = reverse("accounts:api-v1:token_login")
        response = client.post(
            url, data={"email": "test@test.com", "password": "!@#12345"}
        )
        token = Token.objects.get(user=verified_user)
        assert response.status_code == 200
        assert response.data["token"] == token.key

    def test_token_logout_success(self, token_auth_client):
        url = reverse("accounts:api-v1:token_logout")
        response = token_auth_client.post(url)
        assert response.status_code == 204

    def test_token_logout_failure_not_authorized(self, client):
        url = reverse("accounts:api-v1:token_logout")
        response = client.post(url)
        assert response.status_code == 401

    def test_jwt_create(self, client, verified_user):
        url = reverse("accounts:api-v1:jwt_create")
        response = client.post(
            url, data={"email": "test@test.com", "password": "!@#12345"}
        )
        assert response.status_code == 200
        assert response.data["access"]
        assert response.data["user_id"] == verified_user.id

    def test_jwt_refresh_with_valid_refresh_token(self, client, jwt_token):
        url = reverse("accounts:api-v1:jwt_refresh")
        response = client.post(url, data={"refresh": jwt_token["refresh"]})
        assert response.status_code == 200

    def test_jwt_refresh_with_invalid_refresh_token(self, client, jwt_token):
        url = reverse("accounts:api-v1:jwt_refresh")
        response = client.post(url, data={"refresh": jwt_token["refresh"] + "s"})
        assert response.status_code == 401

    def test_jwt_verify_for_valid_token(self, client, jwt_token):
        url = reverse("accounts:api-v1:jwt_verify")
        response = client.post(url, data={"token": jwt_token["access"]})
        assert response.status_code == 200

    def test_jwt_for_unvalid_token(self, client, jwt_token):
        url = reverse("accounts:api-v1:jwt_verify")
        response = client.post(url, data={"token": jwt_token["access"] + "s"})
        assert response.status_code == 401

    def test_user_activation(self, client, user_activation_token, unverified_user):
        url = reverse(
            "accounts:api-v1:activation", kwargs={"token": user_activation_token}
        )
        response = client.get(url)
        response1 = client.get(url)
        user = User.objects.get(email="test1@test.com")
        assert response.status_code == 200
        assert user.is_verified == True
        assert response1.status_code == 400

    def test_user_activation_resend_unverified_user(self, client, unverified_user):
        url = reverse("accounts:api-v1:activation_resend")
        response = client.post(url, data={"email": unverified_user.email})
        assert response.status_code == 200

    def test_user_activation_resend_verified_user_fail(self, client, verified_user):
        url = reverse("accounts:api-v1:activation_resend")
        response = client.post(url, data={"email": verified_user.email})
        assert response.status_code == 400

    def test_profile_view_authorized_verified_user(self, client, verified_user):
        url = reverse("accounts:api-v1:profile")
        client.force_login(user=verified_user)
        response = client.get(url)
        assert response.status_code == 200
        assert response.data["email"] == verified_user.email

    def test_profile_view_authorized_unverified_user_forbidden(
        self, client, unverified_user
    ):
        url = reverse("accounts:api-v1:profile")
        client.force_login(user=unverified_user)
        response = client.get(url)
        assert response.status_code == 403

    def test_profile_view_unauthorized(self, client):
        url = reverse("accounts:api-v1:profile")
        response = client.get(url)
        assert response.status_code == 401

    def test_user_profile_put_data_success(self, client, verified_user):
        url = reverse("accounts:api-v1:profile")
        client.force_login(user=verified_user)
        response = client.put(
            url, data={"first_name": "testname", "last_name": "testlastname"}
        )
        profile = Profile.objects.get(user=verified_user)
        assert response.status_code == 200
        assert response.data["first_name"] == "testname"
        assert profile.first_name == "testname"

    def test_change_password_success(self, client, verified_user):
        url = reverse("accounts:api-v1:change_password")
        client.force_login(user=verified_user)
        response = client.put(
            url,
            data={
                "old_password": "!@#12345",
                "new_password": "12345!@#",
                "new_password1": "12345!@#",
            },
        )
        assert response.status_code == 200

    def test_change_password_wrong_old_password(self, client, verified_user):
        url = reverse("accounts:api-v1:change_password")
        client.force_login(user=verified_user)
        response = client.put(
            url,
            data={
                "old_password": "!@#!@#!@#",
                "new_password": "12345!@#",
                "new_password1": "12345!@#",
            },
        )
        assert response.status_code == 400

    def test_reset_password_request_user_exist(self, client, verified_user):
        url = reverse("accounts:api-v1:request_reset_password")
        response = client.post(url, data={"email": verified_user.email})
        assert response.status_code == 200

    def test_reset_password_request_user_not_exist_fail(self, client):
        url = reverse("accounts:api-v1:request_reset_password")
        response = client.post(url, data={"email": "not_exist@user.com"})
        assert response.status_code == 400

    def test_reset_password_verify_valid_token_to_update_password(
        self, client, verified_user, user_reset_password_token
    ):
        uidb64 = user_reset_password_token["uidb64"]
        token = user_reset_password_token["token"]
        url = reverse(
            "accounts:api-v1:confirm_reset_password",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = client.get(url)
        assert response.status_code == 202

    def test_reset_password_verify_invalid_token_to_update_password(
        self, client, verified_user, user_reset_password_token
    ):
        uidb64 = user_reset_password_token["uidb64"]
        token = user_reset_password_token["token"] + "#"
        url = reverse(
            "accounts:api-v1:confirm_reset_password",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = client.get(url)
        assert response.status_code == 400

    def test_reset_password_update_password_with_valid_token(
        self, client, verified_user, user_reset_password_token
    ):
        uidb64 = user_reset_password_token["uidb64"]
        token = user_reset_password_token["token"]
        url = reverse(
            "accounts:api-v1:confirm_reset_password",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = client.put(
            url, data={"new_password": "!!@@##12345", "new_password1": "!!@@##12345"}
        )
        assert response.status_code == 200

    def test_reset_password_update_password_with_invalid_token(
        self, client, verified_user, user_reset_password_token
    ):
        uidb64 = user_reset_password_token["uidb64"] + "#"
        token = user_reset_password_token["token"]
        url = reverse(
            "accounts:api-v1:confirm_reset_password",
            kwargs={"uidb64": uidb64, "token": token},
        )
        response = client.put(
            url, data={"new_password": "!!@@##12345", "new_password1": "!!@@##12345"}
        )
        assert response.status_code == 200
