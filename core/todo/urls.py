from django.urls import path, include
from .views import *

app_name = 'todo'

urlpatterns = [
    path("", TaskList.as_view(), name="task_list"),
    path("create/", TaskCreate.as_view(), name="task_create"),
    path("edit/<int:pk>/", TaskEdit.as_view(), name="task_edit"),
    path("done/<int:pk>/", TaskDone.as_view(), name="task_done"),
    path("undo/<int:pk>/", TaskUndo.as_view(), name="task_undo"),
    path("delete/<int:pk>/", TaskDelete.as_view(), name="task_delete"),
    path('api/v1/', include('todo.api.v1.urls'))
]