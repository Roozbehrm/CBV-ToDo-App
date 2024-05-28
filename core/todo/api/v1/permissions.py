from rest_framework import permissions

class IsVerified(permissions.BasePermission):
    message = 'User is not verified.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_verified)