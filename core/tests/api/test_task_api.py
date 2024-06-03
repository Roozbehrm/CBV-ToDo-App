import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from todo.models import Task
from accounts.models import Profile


@pytest.mark.django_db
class TestTaskApi:

    def test_get_tasks_response_status_401_unauthorized(self, client):
        url = reverse("todo:api-v1:task-list")
        response = client.get(url)
        assert response.status_code == 401

    def test_get_tasks_response_loggedin_verified_user_200(self, client, verified_user):
        user = verified_user
        client.force_login(user=user)
        url = reverse("todo:api-v1:task-list")
        response = client.get(url)
        assert response.status_code == 200

    def test_get_tasks_response_loggedin_unverified_user_403(
        self, client, unverified_user
    ):
        user = unverified_user
        client.force_login(user=user)
        url = reverse("todo:api-v1:task-list")
        response = client.get(url)
        assert response.status_code == 403

    def test_task_detail_response_loggedin_verified_user_200(
        self, client, verified_user, task
    ):
        user = verified_user
        client.force_authenticate(user=user)
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.id})
        response = client.get(url)
        assert response.status_code == 200

    def test_task_create_response_loggedin_verified_user_200(
        self, client, verified_user
    ):
        user = verified_user
        profile = Profile.objects.get(user__id=user.id)
        client.force_login(user=user)
        url = reverse("todo:api-v1:task-list")
        data = {
            "profile": profile,
            "title": "hello",
        }
        response = client.post(url, data=data)
        assert response.status_code == 201
        assert response.data["title"] == "hello"
        assert response.data["done"] == False

    def test_task_put_response_loggedin_verified_user_200(
        self, client, verified_user, task
    ):
        user = verified_user
        client.force_login(user=user)
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.id})
        response = client.put(url, data={"title": "test1", "description": "test2"})
        assert Task.objects.get(pk=task.id).title == "test1"
        assert response.status_code == 200

    def test_task_patch_response_loggedin_verified_user_200(
        self, client, verified_user, task
    ):
        user = verified_user
        client.force_login(user=user)
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.id})
        response = client.patch(url, data={"description": "test3"})
        assert Task.objects.get(pk=task.id).description == "test3"
        assert response.status_code == 200

    def test_task_delete_response_loggedin_verified_user_200(
        self, client, verified_user, task
    ):
        user = verified_user
        client.force_login(user=user)
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.id})
        response = client.delete(url)
        assert response.status_code == 204
