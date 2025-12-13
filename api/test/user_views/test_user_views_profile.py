from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from api.models import Researcher, Collaborator, Company
from rest_framework.authtoken.models import Token

User = get_user_model()

class ProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Usuário Pesquisador
        self.researcher_user = User.objects.create_user(
            email="researcher@example.com",
            password="password123",
            user_type="researcher"
        )
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher_user,
            firstName="Ana",
            surname="Silva",
            birthDate=date(1980, 5, 5),
            campus="Campus X"
        )
        self.researcher_token = Token.objects.create(user=self.researcher_user)

        # Usuário Colaborador
        self.collaborator_user = User.objects.create_user(
            email="collaborator@example.com",
            password="password123",
            user_type="collaborator"
        )
        self.collaborator_profile = Collaborator.objects.create(
            user=self.collaborator_user,
            firstName="Carlos",
            surname="Souza",
            birthDate=date(1990, 1, 1),
            category="Engenheiro"
        )
        self.collaborator_token = Token.objects.create(user=self.collaborator_user)

        # Usuário Empresa
        self.company_user = User.objects.create_user(
            email="company@example.com",
            password="password123",
            user_type="company"
        )
        self.company_profile = Company.objects.create(
            user=self.company_user,
            fantasyName="Tech Solutions",
            cnpj="12.345.678/0001-99",
            size="Média"
        )
        self.company_token = Token.objects.create(user=self.company_user)

    def test_profile_unauthenticated(self):
        """ Testa que um usuário não autenticado recebe um erro 401. """
        url = reverse("user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_profile_authenticated_researcher(self):
        """ Testa o perfil para um usuário pesquisador autenticado. """
        url = reverse("user-profile")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.researcher_token.key}")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.researcher_user.email)
        self.assertEqual(data["user_type"], "researcher")
        self.assertEqual(data["profile"]["id"], self.researcher_profile.id)

    def test_profile_authenticated_collaborator(self):
        """ Testa o perfil para um usuário colaborador autenticado. """
        url = reverse("user-profile")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.collaborator_token.key}")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.collaborator_user.email)
        self.assertEqual(data["user_type"], "collaborator")
        self.assertEqual(data["profile"]["id"], self.collaborator_profile.id)

    def test_profile_authenticated_company(self):
        """ Testa o perfil para um usuário empresa autenticado. """
        url = reverse("user-profile")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.company_token.key}")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.company_user.email)
        self.assertEqual(data["user_type"], "company")
        self.assertEqual(data["profile"]["id"], self.company_profile.id)
    
    def test_profile_view_with_no_profile_object(self):
        """ Testa o que acontece quando o usuário não tem um objeto de perfil associado. """
        user_no_profile = User.objects.create_user(
            email="noprofile@example.com",
            password="password123",
            user_type="researcher"  # Tipo definido, mas sem objeto Researcher criado
        )
        token_no_profile = Token.objects.create(user=user_no_profile)

        url = reverse("user-profile")
        # Espera-se uma exceção não tratada, que resultará em um erro 500
        with self.assertRaises(Researcher.DoesNotExist):
            self.client.get(url, HTTP_AUTHORIZATION=f"Token {token_no_profile.key}")

    def test_profile_view_with_unhandled_user_type(self):
        """ Testa o perfil para um usuário com um user_type não tratado. """
        unhandled_user = User.objects.create_user(
            email="unhandled@example.com",
            password="password123",
            user_type="admin"  # Um tipo que não é 'researcher', 'collaborator', ou 'company'
        )
        unhandled_token = Token.objects.create(user=unhandled_user)

        url = reverse("user-profile")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {unhandled_token.key}")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], unhandled_user.email)
        self.assertEqual(data["user_type"], "admin")
        self.assertIsNone(data["profile"])
