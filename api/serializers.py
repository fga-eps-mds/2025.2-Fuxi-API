import re
from rest_framework import serializers
from .models import Researcher, Collaborator, Company

class ResearcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Researcher
        fields = ['id', 'email', 'password', 'firstName', 'surname', 'birthDate', 'campus']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if not value.endswith('@unb.br'):
            raise serializers.ValidationError("O e-mail informado não é institucional.")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return value
    
    def validate_birthDate(self, value):
      from datetime import date
      today = date.today()
      if value >= today:
        raise serializers.ValidationError("A data de nascimento deve ser uma data passada.")
      age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
      if age < 18:
        raise serializers.ValidationError("O usuário deve ser maior de 18 anos.")
      return value

class CollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = ['id', 'email', 'password', 'firstName', 'surname', 'birthDate', 'category']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
      if len(value) < 8:
          raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
      return value

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'email', 'password', 'fantasyName', 'cnpj', 'size']
        extra_kwargs = {'password': {'write_only': True}}

    
    def validate_cnpj(self, value):
      cnpj = re.sub(r'\D', '', value)

      if len(cnpj) != 14:
          raise serializers.ValidationError("CNPJ deve ter 14 dígitos.")

      def calculate_digit(cnpj, digit):
          if digit == 1:
              weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
              numbers = cnpj[:12]
          else:
              weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
              numbers = cnpj[:13]

          total = sum(int(n) * w for n, w in zip(numbers, weights))
          remainder = total % 11
          return '0' if remainder < 2 else str(11 - remainder)

      if calculate_digit(cnpj, 1) != cnpj[12] or calculate_digit(cnpj, 2) != cnpj[13]:
          raise serializers.ValidationError("CNPJ inválido.")

      return value


    def validate_password(self, value):
      if len(value) < 8:
          raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
      return value

