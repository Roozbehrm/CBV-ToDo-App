# from rest_framework.decorators import api_view
# from rest_framework.generics import GenericAPIView
from .serializers import TaskSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsVerified
from ...models import Task
from accounts.models import Profile


# ModelViewSet class for list, create, update and delete actions with filtering, sorting and searching features
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsVerified]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["done"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_date"]

    # overriding get_queryset func for getting just tasks of profile related to loggedin User
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        user_tasks = Task.objects.filter(profile=user_profile)
        return user_tasks
