from django.test import TestCase
from api.models import User, Researcher, Research, FavoriteResearch
from datetime import date

class FavoriteResearchModelTestCase(TestCase):
    def test_favorite_research_str_representation(self):
        """Testa a representação em string do modelo FavoriteResearch."""
        # Crie um usuário e um perfil de pesquisador
        user = User.objects.create_user(
            email="testuser@example.com", password="password", user_type="researcher"
        )
        researcher_profile = Researcher.objects.create(
            user=user,
            firstName="Test",
            surname="Researcher",
            birthDate=date(1990, 1, 1),
            campus="Test Campus"
        )
        
        # Crie uma pesquisa
        research = Research.objects.create(
            researcher=researcher_profile,
            title="Test Research Title",
            description="A description",
            status="Ongoing",
            knowledge_area="Science",
            campus="Test Campus"
        )
        
        # Crie o objeto FavoriteResearch
        favorite = FavoriteResearch.objects.create(user=user, research=research)
        
        # Verifique a representação em string
        expected_str = f"{user.email} → {research.title}"
        self.assertEqual(str(favorite), expected_str)
