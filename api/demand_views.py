from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Demand
from django.db.models import Q
from .serializers import (
    DemandSerializer
)

class DemandListPublicView(generics.ListAPIView):
    queryset = Demand.objects.all()
    serializer_class = DemandSerializer
    permission_classes = [AllowAny]

class DemandDetailPublicView(generics.RetrieveAPIView):
    queryset = Demand.objects.all()
    serializer_class = DemandSerializer
    permission_classes = [AllowAny]


class DemandListCreateView(generics.ListCreateAPIView):
    queryset = Demand.objects.all()
    serializer_class = DemandSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type != 'company':
            raise PermissionDenied("Apenas empresas podem visualizar suas próprias demandas.")

        return Demand.objects.filter(company=user.company_profile)

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type != 'company':
            raise PermissionDenied("O usuário não possui permissões para criar uma demanda!")

        company = user.company_profile

        serializer.save(company=company)


class DemandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Demand.objects.all()
    serializer_class = DemandSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        if user.user_type != 'company':
            raise PermissionDenied("Apenas pesquisadores podem editar pesquisas.")

        demand = self.get_object()

        if demand.company != user.company_profile:
            raise PermissionDenied("Você não tem permissão para editar esta pesquisa.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.user_type != 'company':
            raise PermissionDenied("Apenas pesquisadores podem apagar pesquisas.")

        if instance.company != user.company_profile:
            raise PermissionDenied("Você não tem permissão para apagar esta pesquisa.")

        instance.delete()
