from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class LogoutViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="logout@example.com",
            password="12345"
        )

        self.token = Token.objects.create(user=self.user)

    def test_logout_success(self):
        url = reverse("user-logout")
        response = self.client.post(url, HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_without_token(self):
        url = reverse("user-logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)
