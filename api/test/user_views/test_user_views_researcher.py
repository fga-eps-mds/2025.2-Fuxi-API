from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from api.models import Researcher

User = get_user_model()


class ResearcherViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="test@example.com",
            password="12345",
            user_type="researcher"
        )

        self.researcher = Researcher.objects.create(
            user=self.user,
            firstName="Test",
            surname="Researcher",
            birthDate=date(1990, 1, 1),
            campus="Test Campus"
        )

    def test_researcher_detail_view_status_code(self):
        url = reverse("researcher-detail", args=[self.researcher.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_researcher_detail_view_returns_json(self):
        url = reverse("researcher-detail", args=[self.researcher.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["id"], self.researcher.pk)
        self.assertEqual(data["firstName"], self.researcher.firstName)
        self.assertEqual(data["surname"], self.researcher.surname)
        self.assertEqual(data["campus"], self.researcher.campus)

    def test_researcher_detail_not_found(self):
        url = reverse("researcher-detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
