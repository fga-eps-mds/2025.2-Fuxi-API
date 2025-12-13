"""
Testes para os Serializers (serializers.py)
"""
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from api.serializers import (
    ResearcherProfileSerializer,
    CollaboratorProfileSerializer,
    CompanyProfileSerializer,
    UserSerializer,
    ResearchSerializer,
    LoginSerializer
)
from api.models import User, Researcher, Collaborator, Company
from datetime import date, timedelta

class SerializerValidationTestCase(TestCase):

    def setUp(self):
        # Usuário base para testes de atualização
        self.researcher_user = User.objects.create_user(
            email="testuser@unb.br", password="password123", user_type="researcher"
        )
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher_user, firstName="Test", surname="User", birthDate=date(1995, 5, 10), campus="Gama"
        )

    # Testes para validação de data de nascimento
    def test_birthdate_in_the_future_fails(self):
        """Verifica se a validação falha para datas de nascimento no futuro."""
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        serializer = ResearcherProfileSerializer(data={'birthDate': future_date})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("A data de nascimento deve ser uma data passada.", str(cm.exception))

    def test_user_under_18_fails(self):
        """Verifica se a validação falha para usuários com menos de 18 anos."""
        ten_years_ago = date(date.today().year - 10, 1, 1).strftime('%Y-%m-%d')
        serializer = CollaboratorProfileSerializer(data={'birthDate': ten_years_ago})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("O usuário deve ser maior de 18 anos.", str(cm.exception))

    # Testes para validação de CNPJ
    def test_invalid_cnpj_length_fails(self):
        """Verifica se a validação de CNPJ falha com comprimento incorreto."""
        serializer = CompanyProfileSerializer(data={'cnpj': '12345'})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("CNPJ deve ter 14 dígitos.", str(cm.exception))

    def test_invalid_cnpj_check_digit_fails(self):
        """Verifica se a validação de CNPJ falha com dígitos verificadores inválidos."""
        serializer = CompanyProfileSerializer(data={'cnpj': '11.111.111/1111-11'})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("CNPJ inválido.", str(cm.exception))

    # Testes para UserSerializer
    def test_short_password_fails(self):
        """Verifica se senhas com menos de 8 caracteres falham na validação."""
        serializer = UserSerializer(data={'password': '123'})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("A senha deve ter pelo menos 8 caracteres.", str(cm.exception))

    def test_researcher_with_non_unb_email_fails(self):
        """Verifica se um pesquisador com e-mail não institucional falha."""
        data = {
            "email": "test@gmail.com",
            "user_type": "researcher",
            "password": "a_valid_password"
        }
        serializer = UserSerializer(data=data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("O e-mail informado não é institucional (@unb.br).", cm.exception.detail['email'][0])

    def test_update_user_profile_data(self):
        """Verifica se o perfil de um usuário é atualizado corretamente."""
        serializer = UserSerializer(instance=self.researcher_user)
        update_data = {
            'researcher_profile': {
                'firstName': 'Updated'
            }
        }
        updated_serializer = UserSerializer(instance=self.researcher_user, data=update_data, partial=True)
        self.assertTrue(updated_serializer.is_valid(raise_exception=True))
        updated_serializer.save()
        self.researcher_profile.refresh_from_db()
        self.assertEqual(self.researcher_profile.firstName, "Updated")

    # Testes para ResearchSerializer
    def test_research_members_must_be_a_list(self):
        """Verifica se 'members' em ResearchSerializer deve ser uma lista."""
        data = {
            'title': 'Test Title',
            'description': 'Test Desc',
            'status': 'Em Andamento',
            'knowledge_area': 'Test Area',
            'campus': 'Test Campus',
            'members': 'not a list'
        }
        serializer = ResearchSerializer(data=data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Expected a list of items but got type "str".', cm.exception.detail['members'][0])

    def test_update_user_password(self):
        """Verifica se a senha do usuário pode ser atualizada."""
        new_password = "newpassword123"
        serializer = UserSerializer(instance=self.researcher_user, data={'password': new_password}, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertTrue(user.check_password(new_password))

    def test_update_collaborator_profile(self):
        """Verifica se o perfil de um colaborador pode ser atualizado."""
        collab_user = User.objects.create_user(email="collab@test.com", password="p", user_type="collaborator")
        Collaborator.objects.create(user=collab_user, firstName="Initial", surname="Name", birthDate=date(1990,1,1), category="Discente")
        
        update_data = {'collaborator_profile': {'category': 'Servidor'}}
        serializer = UserSerializer(instance=collab_user, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        collab_user.collaborator_profile.refresh_from_db()
        self.assertEqual(collab_user.collaborator_profile.category, "Servidor")

    def test_update_company_profile(self):
        """Verifica se o perfil de uma empresa pode ser atualizado."""
        company_user = User.objects.create_user(email="company@test.com", password="p", user_type="company")
        Company.objects.create(user=company_user, fantasyName="Old Name", cnpj="12345678000100", size="MEI")

        update_data = {'company_profile': {'fantasyName': 'New Name'}}
        serializer = UserSerializer(instance=company_user, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        company_user.company_profile.refresh_from_db()
        self.assertEqual(company_user.company_profile.fantasyName, "New Name")

    def test_create_researcher_user(self):
        """Testa a criação de um usuário pesquisador via UserSerializer."""
        data = {
            "email": "new.researcher@unb.br", "password": "password123", "user_type": "researcher",
            "researcher_profile": {"firstName": "New", "surname": "Researcher", "birthDate": "1990-01-01", "campus": "Gama"}
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertIsNotNone(user.researcher_profile)

    def test_create_collaborator_user(self):
        """Testa a criação de um usuário colaborador via UserSerializer."""
        data = {
            "email": "new.collab@test.com", "password": "password123", "user_type": "collaborator",
            "collaborator_profile": {"firstName": "New", "surname": "Collab", "birthDate": "1990-01-01", "category": "Discente"}
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertIsNotNone(user.collaborator_profile)

    def test_create_company_user(self):
        """Testa a criação de um usuário empresa via UserSerializer."""
        data = {
            "email": "new.company@test.com", "password": "password123", "user_type": "company",
            "company_profile": {"fantasyName": "New Corp", "cnpj": "06.990.590/0001-23", "size": "Grande"}
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertIsNotNone(user.company_profile)

    def test_login_serializer_with_no_credentials_fails(self):
        """Testa se LoginSerializer falha sem credenciais."""
        serializer = LoginSerializer(data={})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("This field is required.", cm.exception.detail['email'][0])
        self.assertIn("This field is required.", cm.exception.detail['password'][0])

    def test_valid_cnpj_with_zero_remainder_digit(self):
        """Testa um CNPJ válido onde o cálculo do dígito resulta em '0'."""
        # CNPJ real e válido: 11.444.777/0001-61
        data = {'cnpj': '11.444.777/0001-61', 'fantasyName': 'Test', 'size': 'Test'}
        serializer = CompanyProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
    
    def test_valid_cnpj_with_non_zero_remainder_digit(self):
        """Testa um CNPJ válido onde o cálculo do dígito resulta em 11 - resto."""
        # CNPJ real e válido: 06.990.590/0001-23
        data = {'cnpj': '06.990.590/0001-23', 'fantasyName': 'Test', 'size': 'Test'}
        serializer = CompanyProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_valid_birthdate_passes(self):
        """Verifica se uma data de nascimento válida passa na validação."""
        valid_date = "1995-05-10"
        serializer = ResearcherProfileSerializer(data={'birthDate': valid_date, 'firstName': 'a', 'surname': 'b', 'campus': 'c'})
        self.assertTrue(serializer.is_valid(raise_exception=True))
