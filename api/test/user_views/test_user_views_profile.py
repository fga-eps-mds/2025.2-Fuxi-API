from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from api.models import Researcher
from rest_framework.authtoken.models import Token

User = get_user_model()

class ProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="prof@example.com",
            password="12345",
            user_type="researcher"
        )

        self.researcher = Researcher.objects.create(
            user=self.user,
            firstName="Ana",
            surname="Silva",
            birthDate=date(1980, 5, 5),
            campus="Campus X"
        )

        self.token = Token.objects.create(user=self.user)

    def test_profile_authenticated(self):
        url = reverse("user-profile")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["profile"]["id"], self.researcher.id)

    def test_profile_unauthenticated(self):
        url = reverse("user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
