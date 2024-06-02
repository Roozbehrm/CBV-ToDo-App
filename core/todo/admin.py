from django.contrib import admin
from .models import Task

# Register your models here.


class TaskAdmin(admin.ModelAdmin):
    models = Task
    ordering = ("-created_date",)
    list_filter = ("profile",)


admin.site.register(Task, TaskAdmin)
