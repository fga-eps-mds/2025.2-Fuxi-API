import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User, Researcher, Collaborator, Company, Research, FavoriteResearch, Demand
from datetime import date

class ResearcherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Researcher
        fields = ['id', 'firstName', 'surname', 'birthDate', 'campus']

    def validate_birthDate(self, value):
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("A data de nascimento deve ser uma data passada.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("O usuário deve ser maior de 18 anos.")
        return value

class CollaboratorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = ['id', 'firstName', 'surname', 'birthDate', 'category']

    def validate_birthDate(self, value):
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("A data de nascimento deve ser uma data passada.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("O usuário deve ser maior de 18 anos.")
        return value

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'fantasyName', 'cnpj', 'size']

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

class UserSerializer(serializers.ModelSerializer):
    researcher_profile = ResearcherProfileSerializer(required=False)
    collaborator_profile = CollaboratorProfileSerializer(required=False)
    company_profile = CompanyProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'user_type', 
                  'researcher_profile', 'collaborator_profile', 'company_profile']
        
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return value
    
    def validate(self, attrs):
        user_type = attrs.get('user_type')
        email = attrs.get('email')

        if user_type == 'researcher' and not email.endswith('@unb.br'):
            raise serializers.ValidationError({"email": "O e-mail informado não é institucional (@unb.br)."})
        return attrs

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        password = validated_data.pop('password')
        profile_data = None

        if user_type == 'researcher':
            profile_data = validated_data.pop('researcher_profile', None)
        elif user_type == 'collaborator':
            profile_data = validated_data.pop('collaborator_profile', None)
        elif user_type == 'company':
            profile_data = validated_data.pop('company_profile', None)

        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            user_type=user_type
        )

        Token.objects.create(user=user)

        if profile_data:
            if user_type == 'researcher':
                Researcher.objects.create(user=user, **profile_data)
            elif user_type == 'collaborator':
                Collaborator.objects.create(user=user, **profile_data)
            elif user_type == 'company':
                Company.objects.create(user=user, **profile_data)

        return user
    

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password) 

        if instance.user_type == 'researcher' and 'researcher_profile' in validated_data:
            profile_data = validated_data.pop('researcher_profile')
            Researcher.objects.filter(user=instance).update(**profile_data)
        elif instance.user_type == 'collaborator' and 'collaborator_profile' in validated_data:
            profile_data = validated_data.pop('collaborator_profile')
            Collaborator.objects.filter(user=instance).update(**profile_data)
        elif instance.user_type == 'company' and 'company_profile' in validated_data:
            profile_data = validated_data.pop('company_profile')
            Company.objects.filter(user=instance).update(**profile_data)

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Usuário inativo.")
        data['user'] = user
        return data

class ResearchSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Research
        fields = ['id', 'researcher', 'createdDate', 'title', 'description', 'status', 'knowledge_area', 'keywords', 'members', 'campus']
        read_only_fields = ['researcher', 'createdDate']

    def validate_members(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("members deve ser um array.")
        return value

class FavoriteResearchSerializer(serializers.ModelSerializer):
    research = ResearchSerializer(read_only=True)

    class Meta:
        model = FavoriteResearch
        fields = ['id', 'research', 'created_at']

class FavoriteResearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteResearch
        fields = ['id','research']

class DemandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demand
        fields = ['id', 'company', 'createdDate', 'title', 'description', 'knowledge_area']
        read_only_fields = ['company', 'createdDate']