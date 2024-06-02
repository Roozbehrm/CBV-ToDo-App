from django.urls import path, include
from . import views

app_name = "todo"

urlpatterns = [
    path("", views.TaskList.as_view(), name="task_list"),
    path("create/", views.TaskCreate.as_view(), name="task_create"),
    path("edit/<int:pk>/", views.TaskEdit.as_view(), name="task_edit"),
    path("done/<int:pk>/", views.TaskDone.as_view(), name="task_done"),
    path("undo/<int:pk>/", views.TaskUndo.as_view(), name="task_undo"),
    path("delete/<int:pk>/", views.TaskDelete.as_view(), name="task_delete"),
    path("api/v1/", include("todo.api.v1.urls")),
]
