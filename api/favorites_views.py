from rest_framework import generics
from rest_framework.permissions import  IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import FavoriteResearch
from .serializers import (
   FavoriteResearchSerializer, FavoriteResearchCreateSerializer
)

class FavoriteResearchListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteResearchSerializer

    def get_queryset(self):
        return FavoriteResearch.objects.filter(user=self.request.user)


class FavoriteResearchCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteResearchCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        research = serializer.validated_data['research']

        if FavoriteResearch.objects.filter(user=user, research=research).exists():
            raise ValidationError("Você já favoritou esta pesquisa.")

        serializer.save(user=user)


class FavoriteResearchDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteResearchSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return FavoriteResearch.objects.filter(user=self.request.user)