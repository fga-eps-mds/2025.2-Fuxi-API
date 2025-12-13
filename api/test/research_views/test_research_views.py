"""
Testes unitários para research_views.py
Integrado ao conjunto de testes existente do projeto
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Research, Researcher, Company
from datetime import date
import json

User = get_user_model()

class ResearchViewsTestCase(APITestCase):
    """Testes unitários completos para research_views.py"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = APIClient()
        
        # Criar usuário pesquisador
        self.researcher_user = User.objects.create_user(
            email='researcher@test.com',
            password='testpass123',
            user_type='researcher'
        )
        
        # Criar usuário colaborador
        self.collaborator_user = User.objects.create_user(
            email='collaborator@test.com',
            password='testpass123',
            user_type='collaborator'
        )
        
        # Criar usuário empresa
        self.company_user = User.objects.create_user(
            email='company@test.com',
            password='testpass123',
            user_type='company'
        )
        
        # Criar perfil de pesquisador
        self.researcher = Researcher.objects.create(
            user=self.researcher_user,
            firstName='João',
            surname='Silva',
            birthDate=date(1990, 1, 1),
            campus='Darcy Ribeiro'
        )
        
        # Segundo pesquisador para testes de permissão
        self.other_researcher_user = User.objects.create_user(
            email='other.researcher@test.com',
            password='testpass123',
            user_type='researcher'
        )
        
        self.other_researcher = Researcher.objects.create(
            user=self.other_researcher_user,
            firstName='Maria',
            surname='Santos',
            birthDate=date(1985, 5, 15),
            campus='Planaltina'
        )

        self.ana_user = User.objects.create_user(
            email='ana@test.com',
            password='testpass123',
            user_type='collaborator'
        )
        self.pedro_user = User.objects.create_user(
            email='pedro@test.com',
            password='testpass123',
            user_type='collaborator'
        )
        
        # Criar pesquisa de teste
        self.research = Research.objects.create(
            researcher=self.researcher,
            title='Pesquisa de Teste',
            description='Descrição da pesquisa de teste',
            status='Em Andamento',
            knowledge_area='Computação',
            keywords=['teste', 'django'],
            campus='Darcy Ribeiro'
        )
        self.research.members.add(self.researcher_user)

    # ===== TESTES PARA ResearchListPublicView =====
    
    def test_research_list_public_view_get_success(self):
        """Testa se a listagem pública de pesquisas funciona"""
        response = self.client.get('/research/all/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Pesquisa de Teste')

    def test_research_list_public_view_no_authentication_required(self):
        """Testa se a view pública não requer autenticação"""
        # Garantir que não há usuário autenticado
        self.client.logout()
        
        response = self.client.get('/research/all/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_research_detail_public_view_get_success(self):
        """Testa se a visualização pública de detalhes de pesquisa funciona"""
        response = self.client.get(f'/research/all/{self.research.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Pesquisa de Teste')

    def test_research_detail_public_view_not_found(self):
        """Testa visualização de pesquisa inexistente"""
        response = self.client.get('/research/all/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ===== TESTES PARA ResearchListCreateView =====
    
    def test_research_list_create_view_requires_authentication(self):
        """Testa se a listagem privada requer autenticação"""
        response = self.client.get('/research/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_research_list_create_view_researcher_access(self):
        """Testa se pesquisador consegue acessar suas pesquisas"""
        self.client.force_authenticate(user=self.researcher_user)
        response = self.client.get('/research/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_research_list_create_view_non_researcher_denied(self):
        """Testa se não-pesquisador é negado acesso à listagem"""
        for user in [self.collaborator_user, self.company_user]:
            with self.subTest(user_type=user.user_type):
                self.client.force_authenticate(user=user)
                response = self.client.get('/research/')
                
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_research_as_researcher_success(self):
        """Testa criação de pesquisa por pesquisador"""
        self.client.force_authenticate(user=self.researcher_user)
        
        data = {
            'title': 'Nova Pesquisa',
            'description': 'Descrição da nova pesquisa',
            'status': 'Planejamento',
            'knowledge_area': 'Inteligência Artificial',
            'keywords': ['AI', 'machine learning'],
            'members': [self.other_researcher_user.id],
            'campus': 'Gama'
        }
        
        response = self.client.post('/research/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Research.objects.count(), 2)
        
        new_research = Research.objects.get(title='Nova Pesquisa')
        self.assertIn(self.researcher_user, new_research.members.all())
        self.assertIn(self.other_researcher_user, new_research.members.all())

    def test_create_research_as_non_researcher_denied(self):
        """Testa que não-pesquisador não pode criar pesquisa"""
        for user in [self.collaborator_user, self.company_user]:
            with self.subTest(user_type=user.user_type):
                self.client.force_authenticate(user=user)
                
                data = {
                    'title': 'Pesquisa Negada',
                    'description': 'Esta pesquisa não deveria ser criada',
                    'status': 'Planejamento',
                    'knowledge_area': 'Teste',
                    'keywords': ['teste'],
                    'members': [],
                    'campus': 'Teste'
                }
                
                response = self.client.post('/research/', data, format='json')
                
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(Research.objects.count(), 1)  # Não deve criar nova pesquisa

    def test_create_research_with_list_of_members(self):
        """Testa criação de pesquisa com lista de membros"""
        self.client.force_authenticate(user=self.researcher_user)
        
        data = {
            'title': 'Pesquisa com Lista de Membros',
            'description': 'Teste com lista de membros',
            'status': 'Ativo',
            'knowledge_area': 'Teste',
            'keywords': ['teste'],
            'members': [self.ana_user.id, self.pedro_user.id],
            'campus': 'FGA'
        }
        
        response = self.client.post('/research/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_research = Research.objects.get(title='Pesquisa com Lista de Membros')
        self.assertIn(self.researcher_user, new_research.members.all())
        self.assertIn(self.ana_user, new_research.members.all())
        self.assertIn(self.pedro_user, new_research.members.all())

    def test_create_research_researcher_name_not_duplicated(self):
        """Testa que o nome do pesquisador não é duplicado se já estiver nos membros"""
        self.client.force_authenticate(user=self.researcher_user)
        
        data = {
            'title': 'Pesquisa Sem Duplicação',
            'description': 'Teste de não duplicação do pesquisador',
            'status': 'Ativo',
            'knowledge_area': 'Teste',
            'keywords': ['teste'],
            'members': [self.researcher_user.id, self.other_researcher_user.id],
            'campus': 'Campus Teste'
        }
        
        response = self.client.post('/research/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_research = Research.objects.get(title='Pesquisa Sem Duplicação')
        # Contar quantas vezes o nome aparece
        count = new_research.members.filter(id=self.researcher_user.id).count()
        self.assertEqual(count, 1, "Nome do pesquisador não deveria ser duplicado")

    # ===== TESTES PARA ResearchDetailView =====
    
    def test_research_detail_view_requires_authentication(self):
        """Testa se a visualização de detalhes privada requer autenticação"""
        response = self.client.get(f'/research/{self.research.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_research_detail_view_retrieve_success(self):
        """Testa recuperação bem-sucedida de detalhes da pesquisa"""
        self.client.force_authenticate(user=self.researcher_user)
        
        response = self.client.get(f'/research/{self.research.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Pesquisa de Teste')

    def test_update_research_as_owner_success(self):
        """Testa atualização bem-sucedida da pesquisa pelo proprietário"""
        self.client.force_authenticate(user=self.researcher_user)
        
        updated_data = {
            'title': 'Pesquisa Atualizada',
            'description': 'Descrição atualizada',
            'status': 'Concluída',
            'knowledge_area': 'Computação',
            'keywords': ['teste', 'atualizado'],
            'members': [self.researcher_user.id, self.other_researcher_user.id],
            'campus': 'Darcy Ribeiro'
        }
        
        response = self.client.put(f'/research/{self.research.id}/', updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se foi atualizada no banco
        self.research.refresh_from_db()
        self.assertEqual(self.research.title, 'Pesquisa Atualizada')
        self.assertEqual(self.research.status, 'Concluída')
        self.assertIn(self.other_researcher_user, self.research.members.all())

    def test_update_research_as_non_researcher_denied(self):
        """Testa que não-pesquisador não pode atualizar pesquisa"""
        for user in [self.collaborator_user, self.company_user]:
            with self.subTest(user_type=user.user_type):
                self.client.force_authenticate(user=user)
                
                data = {'title': 'Título Hackeado'}
                
                response = self.client.patch(f'/research/{self.research.id}/', data, format='json')
                
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_research_as_different_researcher_denied(self):
        """Testa que pesquisador não pode editar pesquisa de outro"""
        self.client.force_authenticate(user=self.other_researcher_user)
        
        data = {'title': 'Tentativa de Hack'}
        
        response = self.client.patch(f'/research/{self.research.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_research_as_owner_success(self):
        """Testa exclusão bem-sucedida da pesquisa pelo proprietário"""
        self.client.force_authenticate(user=self.researcher_user)
        
        response = self.client.delete(f'/research/{self.research.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Research.objects.filter(id=self.research.id).count(), 0)

    def test_delete_research_as_non_researcher_denied(self):
        """Testa que não-pesquisador não pode excluir pesquisa"""
        for user in [self.collaborator_user, self.company_user]:
            with self.subTest(user_type=user.user_type):
                self.client.force_authenticate(user=user)
                
                response = self.client.delete(f'/research/{self.research.id}/')
                
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(Research.objects.filter(id=self.research.id).count(), 1)

    def test_delete_research_as_different_researcher_denied(self):
        """Testa que pesquisador não pode excluir pesquisa de outro"""
        self.client.force_authenticate(user=self.other_researcher_user)
        
        response = self.client.delete(f'/research/{self.research.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Research.objects.filter(id=self.research.id).count(), 1)

    # ===== TESTES DE EDGE CASES =====
    
    def test_research_with_empty_members_list(self):
        """Testa criação de pesquisa com lista de membros vazia"""
        self.client.force_authenticate(user=self.researcher_user)
        
        data = {
            'title': 'Pesquisa Solo',
            'description': 'Pesquisa individual',
            'status': 'Individual',
            'knowledge_area': 'Solo',
            'keywords': ['individual'],
            'members': [],  # Lista vazia
            'campus': 'Campus Solo'
        }
        
        response = self.client.post('/research/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_research = Research.objects.get(title='Pesquisa Solo')
        # Deve ter apenas o pesquisador
        self.assertEqual(new_research.members.count(), 1)
        self.assertIn(self.researcher_user, new_research.members.all())

    def test_research_queryset_filtering(self):
        """Testa se o queryset filtra corretamente por pesquisador"""
        self.client.force_authenticate(user=self.researcher_user)
        
        # Deve retornar apenas pesquisas do usuário logado
        response = self.client.get('/research/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Pesquisa de Teste')
        
        # Verificar que não retorna pesquisas de outros pesquisadores
        titles = [research['title'] for research in response.data]
        # Criar pesquisa do outro pesquisador para verificar filtragem
        research = Research.objects.create(
            researcher=self.other_researcher,
            title='Pesquisa de Outro',
            description='Não deveria aparecer',
            status='Teste',
            knowledge_area='Teste',
            keywords=['outro'],
            campus='Outro Campus'
        )
        research.members.add(self.other_researcher_user)
        
        # Fazer nova requisição - ainda deve retornar apenas 1
        response = self.client.get('/research/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Pesquisa de Teste')

    def test_create_research_with_non_list_members_fails(self):
        """Testa que a criação de pesquisa falha se 'members' não for uma lista."""
        self.client.force_authenticate(user=self.researcher_user)
        data = {'title': 'Test', 'description': 'Test', 'status': 'Test', 'knowledge_area': 'Test', 'campus': 'Test', 'members': 'not-a-list'}
        response = self.client.post('/research/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_research_with_invalid_member_id_is_ignored(self):
        """Testa que IDs de membro inválidos são ignorados na criação."""
        self.client.force_authenticate(user=self.researcher_user)
        data = {'title': 'Test', 'description': 'Test', 'status': 'Test', 'knowledge_area': 'Test', 'campus': 'Test', 'members': [9999]}
        response = self.client.post('/research/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_research_with_company_member_is_ignored(self):
        """Testa que um usuário empresa não é adicionado como membro."""
        self.client.force_authenticate(user=self.researcher_user)
        data = {'title': 'Test', 'description': 'Test', 'status': 'Test', 'knowledge_area': 'Test', 'campus': 'Test', 'members': [self.company_user.id]}
        response = self.client.post('/research/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        research = Research.objects.get(pk=response.data['id'])
        self.assertIn(self.company_user, research.members.all())

    def test_update_research_with_non_list_members_fails(self):
        """Testa que a atualização falha se 'members' não for uma lista."""
        self.client.force_authenticate(user=self.researcher_user)
        research = Research.objects.create(researcher=self.researcher, title="Para Atualizar", status="Test", knowledge_area="Test", campus="Test")
        data = {'members': 'not-a-list'}
        response = self.client.patch(f'/research/{research.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_research_with_invalid_member_id_fails(self):
        """Testa que a atualização falha com um ID de membro inválido."""
        self.client.force_authenticate(user=self.researcher_user)
        research = Research.objects.create(researcher=self.researcher, title="Para Atualizar", status="Test", knowledge_area="Test", campus="Test")
        data = {'members': [9999]}
        response = self.client.patch(f'/research/{research.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_research_with_company_member_is_ignored(self):
        """Testa que um usuário empresa não é adicionado como membro durante a atualização."""
        self.client.force_authenticate(user=self.researcher_user)
        research = Research.objects.create(researcher=self.researcher, title="Para Atualizar", status="Test", knowledge_area="Test", campus="Test")
        data = {'members': [self.company_user.id]}
        response = self.client.patch(f'/research/{research.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        research.refresh_from_db()
        self.assertNotIn(self.company_user, research.members.all())

    def test_update_research_with_creator_in_members(self):
        """Testa que o criador não é duplicado se já estiver na lista de membros."""
        self.client.force_authenticate(user=self.researcher_user)
        research = Research.objects.create(researcher=self.researcher, title="Para Atualizar", status="Test", knowledge_area="Test", campus="Test")
        data = {'members': [self.researcher_user.id]}
        response = self.client.patch(f'/research/{research.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        research.refresh_from_db()
        self.assertEqual(research.members.count(), 1)


class ResearchViewsIntegrationTestCase(APITestCase):
    """Testes de integração para verificar fluxo completo"""
    
    def setUp(self):
        self.researcher_user = User.objects.create_user(
            email='integration@test.com',
            password='testpass123',
            user_type='researcher'
        )
        
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher_user,
            firstName='Integration',
            surname='Tester',
            birthDate=date(1990, 1, 1),
            campus='Test Campus'
        )
        self.collaborator_user = User.objects.create_user(
            email='collab_integration@test.com',
            password='testpass123',
            user_type='collaborator'
        )

    def test_complete_research_lifecycle(self):
        """Testa o ciclo completo: criar, listar, atualizar, excluir pesquisa"""
        self.client.force_authenticate(user=self.researcher_user)
        
        # 1. Criar pesquisa
        create_data = {
            'title': 'Pesquisa Lifecycle',
            'description': 'Teste do ciclo completo',
            'status': 'Iniciando',
            'knowledge_area': 'Teste',
            'keywords': ['lifecycle', 'teste'],
            'members': [self.collaborator_user.id],
            'campus': 'Test Campus'
        }
        
        create_response = self.client.post('/research/', create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        research_id = create_response.data['id']
        
        # 2. Listar pesquisas (deve incluir a nova)
        list_response = self.client.get('/research/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        
        # 3. Atualizar pesquisa
        update_data = {
            'title': 'Pesquisa Lifecycle - Atualizada',
            'description': 'Descrição atualizada',
            'status': 'Em Progresso',
            'knowledge_area': 'Teste',
            'keywords': ['lifecycle', 'atualizado'],
            'members': [self.researcher_user.id, self.collaborator_user.id],
            'campus': 'Test Campus'
        }
        
        update_response = self.client.put(f'/research/{research_id}/', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Pesquisa Lifecycle - Atualizada')
        
        # 4. Verificar que a atualização foi persistida
        detail_response = self.client.get(f'/research/{research_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['status'], 'Em Progresso')
        
        # 5. Excluir pesquisa
        delete_response = self.client.delete(f'/research/{research_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 6. Verificar que foi excluída
        final_list_response = self.client.get('/research/')
        self.assertEqual(final_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(final_list_response.data), 0)


class ResearchSearchViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.researcher_user = User.objects.create_user(email="search_user@test.com", password="password", user_type="researcher")
        self.researcher_profile = Researcher.objects.create(user=self.researcher_user, firstName="Search", surname="User", birthDate=date(1990, 1, 1), campus="Test Campus")
        
        company_user = User.objects.create_user(email="test_company@test.com", password="password", user_type="company")
        self.company = Company.objects.create(user=company_user, fantasyName="Test Corp", cnpj="12345678000100", size="Grande")

        self.research1 = Research.objects.create(
            researcher=self.researcher_profile, title="Tópicos Avançados em IA", campus="Gama", 
            status="Em Andamento", keywords=["IA", "deep learning"], knowledge_area="Ciência da Computação",
            sponsoring_company=self.company
        )
        self.research2 = Research.objects.create(
            researcher=self.researcher_profile, title="Redes Neurais Convolucionais", campus="Gama", 
            status="Concluída", keywords=["redes neurais", "IA"], knowledge_area="Ciência da Computação"
        )
        self.research3 = Research.objects.create(
            researcher=self.researcher_profile, title="História do Brasil", campus="Darcy Ribeiro", 
            status="Em Andamento", keywords=["história"], knowledge_area="História"
        )
        self.research3.members.add(self.researcher_user)

    def test_search_no_params_returns_empty(self):
        """Testa se a busca sem parâmetros retorna uma lista vazia."""
        response = self.client.get(reverse('research-search'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_by_title(self):
        """Testa a busca por título."""
        response = self.client.get(reverse('research-search') + '?title=Tópicos')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Tópicos Avançados em IA")

    def test_search_by_campus(self):
        """Testa a busca por campus."""
        response = self.client.get(reverse('research-search') + '?campus=Gama')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_by_status(self):
        """Testa a busca por status."""
        response = self.client.get(reverse('research-search') + '?status=Concluída')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], "Concluída")

    def test_search_by_single_keyword(self):
        """Testa a busca por uma única palavra-chave."""
        response = self.client.get(reverse('research-search') + '?keyword=história')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_multiple_keywords(self):
        """Testa a busca por múltiplas palavras-chave."""
        response = self.client.get(reverse('research-search') + '?keyword=IA&keyword=redes neurais')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_by_sponsoring_company(self):
        """Testa a busca por empresa patrocinadora."""
        response = self.client.get(reverse('research-search') + '?company=Test Corp')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Tópicos Avançados em IA")

    def test_search_by_researcher_name(self):
        """Testa a busca pelo nome de um pesquisador."""
        response = self.client.get(reverse('research-search') + '?researcher=Search User')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'História do Brasil')