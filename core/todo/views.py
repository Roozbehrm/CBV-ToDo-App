from django.shortcuts import render
from django.views.generic import  ListView, UpdateView, DeleteView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from accounts.models import Profile
from django.urls import reverse_lazy
from django.shortcuts import redirect
# Create your views here.

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    def get_queryset(self):
        user_profile = Profile.objects.get(user = self.request.user)
        return super().get_queryset().filter(profile=user_profile)
    
    
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description']
    success_url = reverse_lazy('todo:task_list')
    template_name = "todo/task_edit.html"

    def form_valid(self, form):
        user_profile = Profile.objects.get(user = self.request.user)
        form.instance.profile = user_profile
        return super().form_valid(form)
    
class TaskEdit(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description']
    success_url = reverse_lazy('todo:task_list')
    template_name = "todo/task_edit.html"

class TaskDone(LoginRequiredMixin, View):
    model = Task
    success_url = reverse_lazy('todo:task_list')

    def get(self, request, *args, **kwargs):
        object = Task.objects.get(id=kwargs.get("pk"))
        object.done= True
        object.save()
        return redirect(self.success_url)
    

class TaskUndo(LoginRequiredMixin, View):
    model = Task
    success_url = reverse_lazy('todo:task_list')

    def get(self, request, *args, **kwargs):
        object = Task.objects.get(id=kwargs.get("pk"))
        object.done= False
        object.save()
        return redirect(self.success_url)
    

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('todo:task_list')

