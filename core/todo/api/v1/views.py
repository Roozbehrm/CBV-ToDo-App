from rest_framework.decorators import api_view
from rest_framework.response import Response
from ...models import Task
from accounts.models import Profile
from .serializers import TaskSerializer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user_profile = Profile.objects.get(user = self.request.user)
        user_tasks = Task.objects.filter(profile= user_profile)
        return user_tasks
        
        








