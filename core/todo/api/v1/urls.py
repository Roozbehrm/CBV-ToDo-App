from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
app_name = 'api-v1'

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')
urlpatterns = router.urls



# urlpatterns = [
#     path('',TaskViewSet.as_view({'get':'list'}), name="test"), 
# ]