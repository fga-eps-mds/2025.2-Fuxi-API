from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="login@example.com",
            password="12345"
        )

    def test_login_success(self):
        url = reverse("user-login")
        payload = {"email": "login@example.com", "password": "12345"}

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], self.user.email)

    def test_login_invalid(self):
        url = reverse("user-login")
        payload = {"email": "login@example.com", "password": "wrong"}

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 400)

    def test_login_nonexistent_user(self):
        """ Testa o login com um usuário que não existe. """
        url = reverse("user-login")
        payload = {"email": "nonexistent@example.com", "password": "12345"}

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 400)

    def test_login_multiple_times_same_token(self):
        """ Testa que fazer login várias vezes retorna o mesmo token. """
        url = reverse("user-login")
        payload = {"email": "login@example.com", "password": "12345"}

        # Primeiro login
        response1 = self.client.post(url, payload)
        self.assertEqual(response1.status_code, 200)
        token1 = response1.json()["token"]

        # Segundo login
        response2 = self.client.post(url, payload)
        self.assertEqual(response2.status_code, 200)
        token2 = response2.json()["token"]

        self.assertEqual(token1, token2)
