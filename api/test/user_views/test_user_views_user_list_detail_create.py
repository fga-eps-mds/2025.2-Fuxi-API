from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user1@example.com",
            password="12345",
            user_type="researcher"
        )

    def test_user_list_status_code(self):
        url = reverse("users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_detail_status_code(self):
        url = reverse("users-detail", args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_detail_json(self):
        url = reverse("users-detail", args=[self.user.pk])
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data["id"], self.user.pk)
        self.assertEqual(data["email"], self.user.email)

    def test_user_detail_not_found(self):
        url = reverse("users-detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_register(self):
        url = reverse("user-register")
        payload = {
            "email": "new@example.com",
            "password": "abc12345",
            "user_type": "collaborator"
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)

