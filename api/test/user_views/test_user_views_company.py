from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from api.models import Company

User = get_user_model()

class CompanyViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="company@example.com",
            password="12345",
            user_type="company"
        )

        self.company = Company.objects.create(
            user=self.user,
            fantasyName="Test Company",
            cnpj="12.345.678/0001-99",
            size="Test Size"
        )

    def test_company_detail_status_code(self):
        url = reverse("company-detail", args=[self.company.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_detail_json(self):
        url = reverse("company-detail", args=[self.company.pk])
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(data["id"], self.company.pk)
        self.assertEqual(data["fantasyName"], self.company.fantasyName)
        self.assertEqual(data["cnpj"], self.company.cnpj)

    def test_company_detail_not_found(self):
        url = reverse("company-detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
