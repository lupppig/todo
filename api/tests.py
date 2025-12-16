from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, Todo
from django.utils import timezone

from datetime import timedelta


class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("signup")
        self.login_url = reverse("login")

        self.user_data = {
            "email": "testuser@example.com",
            "password": "strongpassword123",
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_user_login_success(self):
        User.objects.create_user(**self.user_data)

        response = self.client.post(self.login_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        User.objects.create_user(**self.user_data)

        response = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": "wrongpass"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TodoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="todo@example.com",
            password="strongpassword123",
        )

        login_response = self.client.post(
            reverse("login"),
            {"email": "todo@example.com", "password": "strongpassword123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.access_token = login_response.data.get("access")
        self.assertIsNotNone(self.access_token, "Login failed: access token missing")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.todo_list_url = reverse("todo-list")

    def test_create_todo_with_status(self):
        future_time = timezone.now() + timedelta(days=1)
        data = {
            "title": "Test Todo",
            "body": "Todo body",
            "expires_at": future_time.isoformat(),
            "status": "pending",
        }

        response = self.client.post(self.todo_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        todo = Todo.objects.first()
        self.assertEqual(todo.status, "pending")
        self.assertEqual(todo.created_by, self.user)
        self.assertEqual(todo.updated_by, self.user)

    def test_get_todos(self):
        future_time = timezone.now() + timedelta(days=1)
        Todo.objects.create(
            title="Sample",
            body="Sample body",
            expires_at=future_time,
            status="pending",
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.get(self.todo_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_todo_status(self):
        future_time = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title="Old title",
            body="Old body",
            expires_at=future_time,
            status="pending",
            created_by=self.user,
            updated_by=self.user,
        )

        url = reverse("todo-detail", args=[todo.id])
        response = self.client.patch(
            url,
            {"status": "in_progress"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        todo.refresh_from_db()
        self.assertEqual(todo.status, "in_progress")
        self.assertEqual(todo.updated_by, self.user)

    def test_expired_todo(self):
        # Set expiration in the past
        past_time = timezone.now() - timedelta(days=1)
        todo = Todo.objects.create(
            title="Expired task",
            body="This task should expire",
            expires_at=past_time,
            status="pending",
            created_by=self.user,
            updated_by=self.user,
        )

        todo.save()
        todo.refresh_from_db()

        self.assertEqual(todo.status, "expired", "Todo did not expire as expected")

    def test_delete_todo(self):
        future_time = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title="Delete me",
            body="Body",
            expires_at=future_time,
            status="pending",
            created_by=self.user,
            updated_by=self.user,
        )

        url = reverse("todo-detail", args=[todo.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 0)


class TodoPermissionTests(APITestCase):
    def test_unauthenticated_access_denied(self):
        response = self.client.get(reverse("todo-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_denied(self):
        future_time = timezone.now() + timedelta(days=1)
        data = {
            "title": "Test",
            "body": "Body",
            "expires_at": future_time.isoformat(),
            "status": "pending",
        }
        response = self.client.post(reverse("todo-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
