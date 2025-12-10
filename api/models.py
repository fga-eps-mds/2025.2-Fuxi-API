from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import ArrayField

class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O usuário deve ter um email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPES = [
        ("researcher", "Researcher"),
        ("collaborator", "Collaborator"),
        ("company", "Company"),
    ]
    username = None
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.user_type})"

class Person(models.Model):
    firstName = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    birthDate = models.DateField()

class Researcher(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="researcher_profile")
    campus = models.CharField(max_length=100)


class Collaborator(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="collaborator_profile")
    category = models.CharField(max_length=100)


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile")
    fantasyName = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=100)
    size = models.CharField(max_length=100)

class Research(models.Model):
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE, related_name="researches")
    sponsoring_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="sponsored_researches")
    createdDate = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=100)
    knowledge_area = models.CharField(max_length=100)
    keywords = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    members = models.ManyToManyField(User, related_name="research_member_of")
    campus = models.CharField(max_length=100)

class FavoriteResearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_researches")
    research = models.ForeignKey(Research, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'research')  # não deixa favoritar duas vezes

    def __str__(self):
        return f"{self.user.email} → {self.research.title}"

class Demand(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="demands")
    createdDate = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    knowledge_area = models.CharField(max_length=100)