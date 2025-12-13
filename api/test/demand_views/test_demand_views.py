"""
Testes para as views de Demand (demand_views.py)
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from api.models import Demand, Company, Researcher
from datetime import date

User = get_user_model()

class DemandViewsTestCase(APITestCase):
    
    def setUp(self):
        """Configuração inicial para os testes de Demand."""
        self.client = APIClient()

        # --- Usuários e Perfis ---
        self.company_user = User.objects.create_user(email="company@test.com", password="password123", user_type="company")
        self.company_profile = Company.objects.create(
            user=self.company_user, fantasyName="Test Corp", cnpj="12345678000199", size="Grande"
        )

        self.other_company_user = User.objects.create_user(email="other@test.com", password="password123", user_type="company")
        self.other_company_profile = Company.objects.create(
            user=self.other_company_user, fantasyName="Other Corp", cnpj="98765432000199", size="Media"
        )

        self.researcher_user = User.objects.create_user(email="researcher@test.com", password="password123", user_type="researcher")
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher_user, firstName="Test", surname="Researcher", birthDate=date(1990, 1, 1), campus="Gama"
        )
        
        # --- Demandas ---
        self.demand1 = Demand.objects.create(
            company=self.company_profile,
            title="Desenvolvimento de IA",
            description="Buscamos especialistas em IA.",
            knowledge_area="Tecnologia"
        )
        
        self.demand2 = Demand.objects.create(
            company=self.other_company_profile,
            title="Pesquisa de Mercado",
            description="Análise de mercado para novo produto.",
            knowledge_area="Marketing"
        )

    # ==== Testes de Listagem e Criação (DemandListCreateView) ====

    def test_company_can_create_demand(self):
        """Verifica se uma empresa pode criar uma demanda."""
        self.client.force_authenticate(user=self.company_user)
        data = {"title": "Nova Demanda", "description": "Detalhes...", "knowledge_area": "Inovação"}
        response = self.client.post(reverse("demand-list-create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Demand.objects.count(), 3)

    def test_non_company_cannot_create_demand(self):
        """Verifica se um pesquisador não pode criar uma demanda."""
        self.client.force_authenticate(user=self.researcher_user)
        data = {"title": "Demanda Proibida", "description": "Não deve ser criada", "knowledge_area": "Segurança"}
        response = self.client.post(reverse("demand-list-create"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_can_list_own_demands(self):
        """Verifica se uma empresa pode listar apenas suas próprias demandas."""
        self.client.force_authenticate(user=self.company_user)
        response = self.client.get(reverse("demand-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.demand1.title)

    def test_non_company_cannot_list_demands_from_private_endpoint(self):
        """Verifica se um pesquisador é bloqueado de listar demandas no endpoint privado."""
        self.client.force_authenticate(user=self.researcher_user)
        response = self.client.get(reverse("demand-list-create"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_unauthenticated_user_cannot_access_private_endpoints(self):
        """Verifica se usuário deslogado não acessa endpoints privados de demanda."""
        response_list = self.client.get(reverse("demand-list-create"))
        response_detail = self.client.get(reverse("demand-detail", kwargs={'pk': self.demand1.pk}))
        self.assertEqual(response_list.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_detail.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==== Testes de Detalhe, Atualização e Exclusão (DemandDetailView) ====

    def test_company_can_update_own_demand(self):
        """Verifica se uma empresa pode atualizar sua própria demanda."""
        self.client.force_authenticate(user=self.company_user)
        data = {"title": "Título Atualizado"}
        response = self.client.patch(reverse("demand-detail", kwargs={'pk': self.demand1.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.demand1.refresh_from_db()
        self.assertEqual(self.demand1.title, "Título Atualizado")

    def test_company_cannot_update_other_demand(self):
        """Verifica se uma empresa não pode atualizar demanda de outra."""
        self.client.force_authenticate(user=self.company_user)
        data = {"title": "Título Hackeado"}
        response = self.client.patch(reverse("demand-detail", kwargs={'pk': self.demand2.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_can_delete_own_demand(self):
        """Verifica se uma empresa pode deletar sua própria demanda."""
        self.client.force_authenticate(user=self.company_user)
        response = self.client.delete(reverse("demand-detail", kwargs={'pk': self.demand1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Demand.objects.count(), 1)
    
    def test_company_cannot_delete_other_demand(self):
        """Verifica se uma empresa não pode deletar demanda de outra."""
        self.client.force_authenticate(user=self.company_user)
        response = self.client.delete(reverse("demand-detail", kwargs={'pk': self.demand2.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_company_cannot_delete_demand(self):
        """Verifica se um pesquisador não pode deletar uma demanda."""
        self.client.force_authenticate(user=self.researcher_user)
        response = self.client.delete(reverse("demand-detail", kwargs={'pk': self.demand1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==== Testes das Views Públicas ====

    def test_public_list_is_accessible(self):
        """Verifica se a lista pública de demandas é acessível por qualquer um."""
        response = self.client.get(reverse("demand-public-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_public_detail_is_accessible(self):
        """Verifica se o detalhe público de uma demanda é acessível."""
        response = self.client.get(reverse("demand-public-list-detail", kwargs={'pk': self.demand1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.demand1.title)

    # ==== Testes da View de Busca (DemandSearchView) ====

    def test_search_with_no_params_returns_none(self):
        """Verifica se a busca sem parâmetros retorna uma lista vazia."""
        response = self.client.get(reverse("demand-search"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_by_title(self):
        """Verifica a busca por título."""
        response = self.client.get(f'{reverse("demand-search")}?title=Desenvolvimento')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.demand1.id)

    def test_search_by_description(self):
        """Verifica a busca por descrição."""
        response = self.client.get(f'{reverse("demand-search")}?description=mercado')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.demand2.id)

    def test_search_by_knowledge_area(self):
        """Verifica a busca por área de conhecimento."""
        response = self.client.get(f'{reverse("demand-search")}?knowledge_area=Tecnologia')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.demand1.id)

    def test_search_by_company_name(self):
        """Verifica a busca por nome da empresa."""
        response = self.client.get(f'{reverse("demand-search")}?company=Test Corp')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.demand1.id)

    def test_search_with_no_results(self):
        """Verifica se uma busca sem resultados retorna lista vazia."""
        response = self.client.get(f'{reverse("demand-search")}?title=Inexistente')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
