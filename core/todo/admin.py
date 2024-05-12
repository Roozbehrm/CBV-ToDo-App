from django.contrib import admin
from .models import Task
# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    models = Task
    ordering = ('-created_date',)

admin.site.register(Task, TaskAdmin)