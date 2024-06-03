from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    ActivationResendSerializer,
    RequestPasswordResetSerializer,
    ResetPasswordConfirmApiSerializer,
    ValidatePasswordResetSerializer,
)
from rest_framework import status, parsers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsVerified
from ...models import Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import update_last_login
from mail_templated import EmailMessage
from ..utils import EmailThread
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import jwt
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class RegistrationApiView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
            user_obj = User.objects.get(email=email)
            token = self.get_token_for_user(user_obj)
            site_address = get_current_site(request)
            activation_url = reverse(
                "accounts:api-v1:activation",
                kwargs={"token": token},
            )
            activation_link = f"http://{site_address}{activation_url}"

            email_msg = EmailMessage(
                "email/user-activation.tpl",
                {"link": activation_link},
                "roozbehm.ir",
                to=[email],
            )
            EmailThread(email_msg).start()

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


# login with token
class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    parser_classes = (parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        update_last_login(None, token.user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


# token logout
class CustomDestroyToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except User.auth_token.RelatedObjectDoesNotExist:
            return Response(
                {"detail": "User has no auth_token."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# jwt create, refresh
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# change password for logged in user
class ChangePasswordApiView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"datails": "password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileApiView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated, IsVerified]

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class ActivationApiView(APIView):

    def get(self, request, token, *args, **kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        except jwt.exceptions.InvalidTokenError:
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = token.get("user_id")
        user_obj = User.objects.get(pk=user_id)
        if user_obj.is_verified:
            return Response(
                {"detail": "Your account is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_obj.is_verified = True
        user_obj.save()

        return Response({"detail": "Your account successfully activated"})


class ActivationResendApiView(GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user_obj"]
        token = self.get_token_for_user(user_obj)
        site_address = get_current_site(request)
        activation_url = reverse(
            "accounts:api-v1:activation",
            kwargs={"token": token},
        )
        activation_link = f"http://{site_address}{activation_url}"

        email_msg = EmailMessage(
            "email/user-activation.tpl",
            {"link": activation_link},
            "roozbehm.ir",
            to=[user_obj.email],
        )
        EmailThread(email_msg).start()
        return Response({"detail": "Activation email resent."})

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


# password reset
class RequestPasswordResetApi(GenericAPIView):
    """
    Request password reset for user by sending email
    """

    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        """
        Create token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            site_address = get_current_site(request)
            reset_url = reverse(
                "accounts:api-v1:confirm_reset_password",
                kwargs={"uidb64": uidb64, "token": 'testfalse'},
            )
            reset_link = f"http://{site_address}{reset_url}"

            # send the rest_link as mail to the user.
            email_msg = EmailMessage(
                "email/reset-password.tpl",
                {"link": reset_link},
                "roozbehm.ir",
                to=[user.email],
            )
            EmailThread(email_msg).start()
            return Response(
                {"detail": "password reset link sent to your email"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordConfirmApi(GenericAPIView):
    """
    Verify and Reset Password Token View.
    """

    serializer_class = ResetPasswordConfirmApiSerializer

    def get(self, request, uidb64, token):
        # uses another serializer to vrify token and uid to
        serializer = ValidatePasswordResetSerializer(
            data={"token": token, "uidb64": uidb64}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "token vrified! Enter new Password"},
            status=status.HTTP_202_ACCEPTED,
        )

    def put(self, request, *args, **kwargs):
        """
        Verify token & uid and then reset the password.
        """

        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "Password reset completed"}, status=status.HTTP_200_OK
        )
