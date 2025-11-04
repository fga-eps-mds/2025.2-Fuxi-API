from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import User, Researcher, Collaborator, Company
from .serializers import (
    ResearcherProfileSerializer,
    CollaboratorProfileSerializer,
    CompanyProfileSerializer,
    LoginSerializer,
    UserSerializer,
)


class ResearcherListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Researcher.objects.all()
    serializer_class = ResearcherProfileSerializer

class ResearcherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Researcher.objects.all()
    serializer_class = ResearcherProfileSerializer



class CollaboratorListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorProfileSerializer

class CollaboratorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorProfileSerializer



class CompanyListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Company.objects.all()
    serializer_class = CompanyProfileSerializer

class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Company.objects.all()
    serializer_class = CompanyProfileSerializer
    

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "email": user.email,
            "user_type": user.user_type,
            "is_authenticated": True
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                return Response({"detail": "Token não encontrado."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_200_OK)
    
