from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Research, Researcher
from datetime import date
import json

User = get_user_model()

class ResearchViewsTestCase(APITestCase):
    def setUp(self):
        """Configuração inicial para os testes"""
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
        
        # Criar perfil de pesquisador
        self.researcher = Researcher.objects.create(
            user=self.researcher_user,
            firstName='João',
            surname='Silva',
            birthDate=date(1990, 1, 1),
            campus='Darcy Ribeiro'
        )
        
        # Criar pesquisa de teste
        self.research = Research.objects.create(
            researcher=self.researcher,
            title='Pesquisa de Teste',
            description='Descrição da pesquisa de teste',
            status='Em Andamento',
            knowledge_area='Computação',
            keywords=['teste', 'django'],
            members=['João Silva'],
            campus='Darcy Ribeiro'
        )

    def test_research_list_public_view_get(self):
        """Testa se a listagem pública de pesquisas funciona"""
        url = reverse('research-list-public')  # Ajuste o nome da URL conforme sua configuração
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Pesquisa de Teste')

    def test_research_detail_public_view_get(self):
        """Testa se a visualização pública de detalhes de pesquisa funciona"""
        url = reverse('research-detail-public', kwargs={'pk': self.research.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Pesquisa de Teste')

    def test_research_list_create_view_requires_authentication(self):
        """Testa se a listagem privada requer autenticação"""
        url = reverse('research-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_research_list_create_view_researcher_access(self):
        """Testa se pesquisador consegue acessar suas pesquisas"""
        self.client.force_authenticate(user=self.researcher_user)
        url = reverse('research-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_research_list_create_view_non_researcher_denied(self):
        """Testa se não-pesquisador é negado acesso à listagem"""
        self.client.force_authenticate(user=self.collaborator_user)
        url = reverse('research-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_research_as_researcher(self):
        """Testa criação de pesquisa por pesquisador"""
        self.client.force_authenticate(user=self.researcher_user)
        url = reverse('research-list-create')
        
        data = {
            'title': 'Nova Pesquisa',
            'description': 'Descrição da nova pesquisa',
            'status': 'Planejamento',
            'knowledge_area': 'Inteligência Artificial',
            'keywords': ['AI', 'machine learning'],
            'members': ['Maria Santos'],
            'campus': 'Gama'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Research.objects.count(), 2)
        
        # Verifica se o nome do pesquisador foi adicionado aos membros
        new_research = Research.objects.get(title='Nova Pesquisa')
        self.assertIn('João Silva', new_research.members)
        self.assertIn('Maria Santos', new_research.members)

    def test_create_research_as_non_researcher_denied(self):
        """Testa que não-pesquisador não pode criar pesquisa"""
        self.client.force_authenticate(user=self.collaborator_user)
        url = reverse('research-list-create')
        
        data = {
            'title': 'Pesquisa Negada',
            'description': 'Esta pesquisa não deveria ser criada',
            'status': 'Planejamento',
            'knowledge_area': 'Teste',
            'keywords': ['teste'],
            'members': [],
            'campus': 'Teste'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Research.objects.count(), 1)  # Não deve criar nova pesquisa

    def test_create_research_with_string_members(self):
        """Testa criação de pesquisa com membros como string JSON"""
        self.client.force_authenticate(user=self.researcher_user)
        url = reverse('research-list-create')
        
        data = {
            'title': 'Pesquisa com Membros String',
            'description': 'Teste com membros como string',
            'status': 'Ativo',
            'knowledge_area': 'Teste',
            'keywords': ['teste'],
            'members': '["Ana Costa", "Pedro Lima"]',  # String JSON
            'campus': 'FGA'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_research = Research.objects.get(title='Pesquisa com Membros String')
        self.assertIn('João Silva', new_research.members)
        self.assertIn('Ana Costa', new_research.members)
        self.assertIn('Pedro Lima', new_research.members)

    def test_update_research_as_owner(self):
        """Testa atualização de pesquisa pelo proprietário"""
        self.client.force_authenticate(user=self.researcher_user)
        url = reverse('research-detail', kwargs={'pk': self.research.id})
        
        data = {
            'title': 'Pesquisa Atualizada',
            'description': 'Descrição atualizada',
            'status': 'Concluída',
            'knowledge_area': 'Computação',
            'keywords': ['teste', 'atualizado'],
            'members': ['João Silva'],
            'campus': 'Darcy Ribeiro'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.research.refresh_from_db()
        self.assertEqual(self.research.title, 'Pesquisa Atualizada')
        self.assertEqual(self.research.status, 'Concluída')

    def test_update_research_as_non_researcher_denied(self):
        """Testa que não-pesquisador não pode atualizar pesquisa"""
        self.client.force_authenticate(user=self.collaborator_user)
        url = reverse('research-detail', kwargs={'pk': self.research.id})
        
        data = {'title': 'Título Hackeado'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_research_as_owner(self):
        """Testa exclusão de pesquisa pelo proprietário"""
        self.client.force_authenticate(user=self.researcher_user)
        url = reverse('research-detail', kwargs={'pk': self.research.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Research.objects.count(), 0)

    def test_delete_research_as_non_researcher_denied(self):
        """Testa que não-pesquisador não pode excluir pesquisa"""
        self.client.force_authenticate(user=self.collaborator_user)
        url = reverse('research-detail', kwargs={'pk': self.research.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Research.objects.count(), 1)

    def test_delete_research_by_different_researcher_denied(self):
        """Testa que pesquisador não pode excluir pesquisa de outro"""
        # Criar outro pesquisador
        other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            user_type='researcher'
        )
        other_researcher = Researcher.objects.create(
            user=other_user,
            firstName='Maria',
            surname='Santos',
            birthDate=date(1985, 5, 15),
            campus='Planaltina'
        )
        
        self.client.force_authenticate(user=other_user)
        url = reverse('research-detail', kwargs={'pk': self.research.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Research.objects.count(), 1)

    def test_research_detail_view_requires_authentication(self):
        """Testa se a visualização de detalhes privada requer autenticação"""
        url = reverse('research-detail', kwargs={'pk': self.research.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
