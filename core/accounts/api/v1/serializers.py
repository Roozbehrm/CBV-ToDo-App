from typing import Dict
from rest_framework import serializers
from ...models import User, Profile
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode


class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password1']


    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password1'):
            raise serializers.ValidationError({'details':'Passwords do not match.'})
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password':list(e.messages)})

        return super().validate(attrs)
    

    def create(self, validated_data):
        validated_data.pop('password1', None)
        return User.objects.create_user(**validated_data)
    

# token authentication
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_verified:
                raise serializers.ValidationError({'detail':'User is not verified.'})
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    
# Jwt Authentication
class  CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if not self.user.is_verified:
                raise serializers.ValidationError({'detail':'User is not verified.'})
        validated_data['user_id'] = self.user.id
        validated_data['email'] = self.user.email
        return validated_data
    

class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password1'):
            raise serializers.ValidationError({'detail':'Passwords do not match.'})
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password':list(e.messages)})

        return super().validate(attrs)
    
    
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id','email','image', 'first_name', 'last_name', 'description']


class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user_obj = User.objects.get(email= email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail':'User does not exist.'})
        if user_obj.is_verified:
             raise serializers.ValidationError({'detail':'User is already verified.'})
        
        attrs['user_obj'] = user_obj
        return super().validate(attrs)


# reset password serializers    
class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Reset Password Email Request Serializer.
    """
    email = serializers.EmailField()

    

class ResetPasswordConfirmApiSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=1,)
    password1 = serializers.CharField(write_only=True, min_length=1,)


    def validate(self, attrs):
        password = attrs.get("password")
        password1 = attrs.get("password1")
        token = self.context.get("kwargs").get("token")
        uidb64 = self.context.get("kwargs").get("uidb64")

        if token is None or uidb64 is None:
            raise serializers.ValidationError({'detail':'Missing data.'})
        try:
            pk = urlsafe_base64_decode(uidb64).decode()
            user_obj = User.objects.get(pk= pk)
        except:
            raise serializers.ValidationError({'detail':'The reset token is invalid.'})
        
        if not PasswordResetTokenGenerator().check_token(user_obj, token):
            raise serializers.ValidationError({'detail':'The reset token is invalid.'})
        
        if password != password1:
            raise serializers.ValidationError({'detail':'Passwords do not match.'})
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password':list(e.messages)})

        user_obj.set_password(password)
        user_obj.save()
        return super().validate(attrs)
    

class ValidatePasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get("token")
        uidb64 = attrs.get("uidb64")
        if token is None or uidb64 is None:
            raise serializers.ValidationError({'detail':'Missing data.'})

        try:
            pk = urlsafe_base64_decode(uidb64).decode()
            user_obj = User.objects.get(pk= pk)
        except:
            raise serializers.ValidationError({'detail':'The reset token is invalid.'})
         
        if not PasswordResetTokenGenerator().check_token(user_obj, token):
            raise serializers.ValidationError({'detail':'The reset token is invalid.'})
        return super().validate(attrs)


    