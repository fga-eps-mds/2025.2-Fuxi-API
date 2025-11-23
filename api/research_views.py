from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Research, FavoriteResearch
from django.db.models import Q
from .serializers import (
    ResearchSerializer, FavoriteResearchSerializer, FavoriteResearchCreateSerializer
)

class ResearchListPublicView(generics.ListAPIView):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = [AllowAny]

class ResearchDetailPublicView(generics.RetrieveAPIView):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = [AllowAny]


class ResearchListCreateView(generics.ListCreateAPIView):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type != 'researcher':
            raise PermissionDenied("Apenas pesquisadores podem visualizar suas próprias pesquisas.")

        return Research.objects.filter(researcher=user.researcher_profile)

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type != 'researcher':
            raise PermissionDenied("O usuário não possui permissões para criar uma pesquisa!")

        researcher = user.researcher_profile

        researcher_name = f"{researcher.firstName} {researcher.surname}".strip()


        members = self.request.data.get("members", [])
        if isinstance(members, str):
            import json
            members = json.loads(members)

        if researcher_name not in members:
            members = [researcher_name] + members

        serializer.save(researcher=researcher, members=members)


class ResearchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        if user.user_type != 'researcher':
            raise PermissionDenied("Apenas pesquisadores podem editar pesquisas.")

        research = self.get_object()

        if research.researcher != user.researcher_profile:
            raise PermissionDenied("Você não tem permissão para editar esta pesquisa.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.user_type != 'researcher':
            raise PermissionDenied("Apenas pesquisadores podem apagar pesquisas.")

        if instance.researcher != user.researcher_profile:
            raise PermissionDenied("Você não tem permissão para apagar esta pesquisa.")

        instance.delete()

class ResearchSearchView(generics.ListAPIView):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = [AllowAny]  

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        title = params.get("title")
        description = params.get("description")
        status = params.get("status")
        knowledge_area = params.get("knowledge_area")
        keywords = params.getlist("keyword")
        campus = params.get("campus")
        researcher_name = params.get("researcher")

        if not any([title, description, status, knowledge_area, keywords, campus, researcher_name]):
            return Research.objects.none()

        if title:
            queryset = queryset.filter(title__icontains=title)

        if description:
            queryset = queryset.filter(description__icontains=description)

        if status:
            queryset = queryset.filter(status__iexact=status)

        if knowledge_area:
            queryset = queryset.filter(knowledge_area__icontains=knowledge_area)

        if keywords:
            kw_filter = Q()
            for kw in keywords:
                kw_filter |= Q(keywords__contains=[kw])
            queryset = queryset.filter(kw_filter)

        if campus:
            queryset = queryset.filter(campus__iexact=campus)

        if researcher_name:
            queryset = queryset.filter(
                Q(members__contains=[researcher_name])
            )

        return queryset