from django.db import models

class BaseUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    class Meta:
        abstract = True

class PersonUser(BaseUser):
    firstName = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    birthDate = models.DateField()

    class Meta:
        abstract = True

class Collaborator(PersonUser):
    category = models.CharField(max_length=100)

class Researcher(PersonUser):
    campus = models.CharField(max_length=100)

class Company(BaseUser):
    fantasyName = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
