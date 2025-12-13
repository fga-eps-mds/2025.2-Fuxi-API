from django.test import TestCase
from api.models import User, Researcher, Collaborator, Company
from datetime import date

class UserModelTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user( 
            email="testemail@example.com",
            password="testpassword",
        )

        self.assertEqual(user.email, "testemail@example.com")
        self.assertTrue(user.check_password("testpassword"))
     
    
    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="testemail@example.com",
            password="testpassword",
        )

        self.assertEqual(superuser.email, "testemail@example.com")
        self.assertTrue(superuser.check_password("testpassword"))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


    def test_create_researcher(self):
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

        self.assertEqual(user.email, "testemail@example.com")
        self.assertEqual(user.user_type, "researcher")
        self.assertTrue(user.check_password("testpassword"))
        self.assertEqual(researcher_profile.firstName, "Test")
        self.assertEqual(researcher_profile.surname, "Researcher")
        self.assertEqual(researcher_profile.birthDate.strftime("%Y-%m-%d"), "1990-01-01")
        self.assertEqual(researcher_profile.campus, "Test Campus")


    def test_create_collaborator(self):
        user = User.objects.create_user(
            email="testemail@example.com",
            password="testpassword",
            user_type="collaborator"
        )
        collaborator_profile = Collaborator.objects.create(
            user=user,
            firstName="Test",
            surname="Collaborator",
            birthDate=date(1990, 1, 1),
            category="Test Category"
        )

        self.assertEqual(user.email, "testemail@example.com")
        self.assertEqual(user.user_type, "collaborator")
        self.assertTrue(user.check_password("testpassword"))
        self.assertEqual(collaborator_profile.firstName, "Test")
        self.assertEqual(collaborator_profile.surname, "Collaborator")
        self.assertEqual(collaborator_profile.birthDate.strftime("%Y-%m-%d"), "1990-01-01")
        self.assertEqual(collaborator_profile.category, "Test Category")


    def test_create_company(self):
        user = User.objects.create_user(
            email="testemail@example.com",
            password="testpassword",
            user_type="company"
        )

        company_profile = Company.objects.create(
            user=user,
            fantasyName="Test Company",
            cnpj="12.345.678/0001-99",
            size="Test Size"
        )

        self.assertEqual(user.email, "testemail@example.com")
        self.assertEqual(user.user_type, "company")
        self.assertTrue(user.check_password("testpassword"))
        self.assertEqual(company_profile.fantasyName, "Test Company")
        self.assertEqual(company_profile.cnpj, "12.345.678/0001-99")
        self.assertEqual(company_profile.size, "Test Size")


    def test_user_str_representation(self):
        user = User.objects.create_user(
            email="testemail@example.com",
            password="testpassword",
            user_type="researcher"
        )

        self.assertEqual(str(user), "testemail@example.com (researcher)")


    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="")


    def test_create_superuser_not_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="testemail@example.com",
                password="testpassword",
                is_staff=False
            )

    def test_create_superuser_not_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="testemail@example.com",
                password="testpassword",
                is_superuser=False
            )
