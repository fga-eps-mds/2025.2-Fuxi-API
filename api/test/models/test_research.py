from django.test import TestCase
from api.models import User, Researcher
from api.models import Research
from datetime import date

class ResearchModelTestCase(TestCase):
    def test_create_research(self):
        user = User.objects.create_user(
            email="testemail@example.com",
            password="testpassword",
            user_type="researcher"
        )

        researcher_profile = Researcher.objects.create(
            user=user,
            firstName="Test",
            surname="Researcher",
            birthDate=date(1990, 1, 1),
            campus="Test Campus"
        )

        research = Research.objects.create(
            researcher=researcher_profile,
            #createdDate=date(2024, 1, 1),
            title="Test Research Title",
            description="This is a test description for the research.",
            status="ongoing",
            knowledge_area="test area",
            keywords="test, research",
            campus="Test Campus"
        )

        self.assertEqual(research.researcher, researcher_profile)

        self.assertEqual(research.researcher.firstName, "Test")
        self.assertEqual(research.researcher.surname, "Researcher")
        self.assertEqual(research.researcher.birthDate.strftime("%Y-%m-%d"), "1990-01-01")
        self.assertEqual(research.researcher.campus, "Test Campus")

        self.assertEqual(research.researcher.user.email, "testemail@example.com")
        self.assertTrue(research.researcher.user.check_password("testpassword"))
        self.assertEqual(research.researcher.user.user_type, "researcher")

        self.assertEqual(research.createdDate.strftime("%Y-%m-%d"), date.today().strftime("%Y-%m-%d"))
        self.assertEqual(research.title, "Test Research Title")
        self.assertEqual(research.description, "This is a test description for the research.")
        self.assertEqual(research.status, "ongoing")
        self.assertEqual(research.knowledge_area, "test area")
        self.assertEqual(research.keywords, "test, research")
        self.assertEqual(research.campus, "Test Campus")