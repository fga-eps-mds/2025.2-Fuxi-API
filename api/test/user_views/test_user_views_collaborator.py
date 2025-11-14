from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from api.models import Collaborator

User = get_user_model()

class CollaboratorViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="test@example.com",
            password="12345",
            user_type="collaborator"
        )

        self.collaborator = Collaborator.objects.create(
            user=self.user,
            firstName="Test",
            surname="Collaborator",
            birthDate=date(1990, 1, 1),
            category="Test Category"
        )

    def test_collaborator_detail_status_code(self):
        url = reverse("collaborator-detail", args=[self.collaborator.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_collaborator_detail_json(self):
        url = reverse("collaborator-detail", args=[self.collaborator.pk])
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(data["id"], self.collaborator.pk)
        self.assertEqual(data["firstName"], self.collaborator.firstName)
        self.assertEqual(data["surname"], self.collaborator.surname)

    def test_collaborator_detail_not_found(self):
        url = reverse("collaborator-detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
