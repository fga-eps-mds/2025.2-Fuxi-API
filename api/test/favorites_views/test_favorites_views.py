"""
Testes para as views de FavoriteResearch (favorites_views.py)
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from api.models import Research, Researcher, FavoriteResearch
from datetime import date

User = get_user_model()

class FavoriteViewsTestCase(APITestCase):

    def setUp(self):
        """Configuração inicial para os testes de Favoritos."""
        self.client = APIClient()

        # --- Usuários e Perfis ---
        self.user1 = User.objects.create_user(email="user1@test.com", password="password123", user_type="researcher")
        self.researcher1_profile = Researcher.objects.create(
            user=self.user1, firstName="User", surname="One", birthDate=date(1990, 1, 1), campus="Gama"
        )

        self.user2 = User.objects.create_user(email="user2@test.com", password="password123", user_type="researcher")
        self.researcher2_profile = Researcher.objects.create(
            user=self.user2, firstName="User", surname="Two", birthDate=date(1991, 1, 1), campus="Gama"
        )
        
        # --- Pesquisas ---
        self.research1 = Research.objects.create(
            researcher=self.researcher1_profile,
            title="Pesquisa sobre IA",
            description="Inteligência Artificial avançada.",
            knowledge_area="Tecnologia"
        )
        
        self.research2 = Research.objects.create(
            researcher=self.researcher2_profile,
            title="Pesquisa sobre Biologia",
            description="Biologia molecular.",
            knowledge_area="Saúde"
        )
        
        # --- Favorito existente ---
        self.existing_favorite = FavoriteResearch.objects.create(user=self.user1, research=self.research2)

    def test_authenticated_user_can_list_favorites(self):
        """Verifica se um usuário autenticado pode listar seus favoritos."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("favorite-list"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['research']['title'], self.research2.title)

    def test_user_sees_only_own_favorites(self):
        """Verifica se um usuário não vê os favoritos de outro usuário."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse("favorite-list"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # user2 não tem favoritos

    def test_unauthenticated_user_cannot_list_favorites(self):
        """Verifica se um usuário não autenticado não pode listar favoritos."""
        response = self.client.get(reverse("favorite-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_can_add_a_favorite(self):
        """Verifica se um usuário pode adicionar uma nova pesquisa aos favoritos."""
        self.client.force_authenticate(user=self.user1)
        data = {'research': self.research1.id}
        response = self.client.post(reverse("favorite-add"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FavoriteResearch.objects.filter(user=self.user1, research=self.research1).exists())
    
    def test_user_cannot_add_same_favorite_twice(self):
        """Verifica se o sistema impede de adicionar o mesmo favorito duas vezes."""
        # user1 já favoritou research2 no setUp
        self.client.force_authenticate(user=self.user1)
        data = {'research': self.research2.id}
        response = self.client.post(reverse("favorite-add"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Você já favoritou esta pesquisa.", response.data)

    def test_user_can_remove_a_favorite(self):
        """Verifica se um usuário pode remover um favorito."""
        self.client.force_authenticate(user=self.user1)
        
        # O ID do favorito é o do objeto FavoriteResearch, não o da pesquisa
        favorite_id = self.existing_favorite.id
        
        response = self.client.delete(reverse("favorite-remove", kwargs={'pk': favorite_id}))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FavoriteResearch.objects.filter(id=favorite_id).exists())

    def test_user_cannot_remove_other_users_favorite(self):
        """Verifica que um usuário não pode remover o favorito de outro."""
        self.client.force_authenticate(user=self.user2)
        favorite_id = self.existing_favorite.id
        
        response = self.client.delete(reverse("favorite-remove", kwargs={'pk': favorite_id}))
        
        # A view filtra o queryset, então o resultado será 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(FavoriteResearch.objects.filter(id=favorite_id).exists())

