from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter


app_name = 'api-v1'

# default Router to generate urls for ModelViewSet
router = DefaultRouter()
router.register('task', TaskViewSet, basename='task')
urlpatterns = router.urls



# urlpatterns = [
#     path('',TaskViewSet.as_view({'get':'list'}), name="test"), 
# ]