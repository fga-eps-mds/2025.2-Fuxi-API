from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import User, Research, FavoriteResearch
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

        if user.user_type != "researcher":
            raise PermissionDenied("Apenas pesquisadores podem criar pesquisas.")

        researcher = user.researcher_profile

        research = serializer.save(researcher=researcher)

        research.members.add(user)

        members_ids = self.request.data.get("members", [])

        if isinstance(members_ids, list):
            for uid in members_ids:
                try:
                    u = User.objects.get(id=uid)
                    if u.user_type != "company":
                        research.members.add(u)
                except User.DoesNotExist:
                    pass 

        research.save()


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
        
        instance = serializer.save()

        if 'members' in self.request.data:
            members_ids = self.request.data.get('members', [])

            if not isinstance(members_ids, list):
                raise ValidationError({"members": "members deve ser uma lista de IDs."})

            new_members = []
            for uid in members_ids:
                try:
                    u = User.objects.get(pk=uid)
                    if u.user_type in ("researcher", "collaborator"):
                        new_members.append(u)
                except User.DoesNotExist:
                    raise ValidationError({"members": f"Usuário com ID {uid} não existe."})
                    continue

            creator_user = research.researcher.user 
            if creator_user not in new_members:
                new_members.insert(0, creator_user)

            instance.members.set(new_members)
            instance.save()

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
        queryset = Research.objects.select_related('sponsoring_company', 'researcher').all()
        params = self.request.query_params

        title = params.get("title")
        description = params.get("description")
        status = params.get("status")
        knowledge_area = params.get("knowledge_area")
        keywords = params.getlist("keyword")
        campus = params.get("campus")
        researcher_name = params.get("researcher")
        sponsoring_company = params.get("company")

        if not any([title, description, status, knowledge_area, keywords, campus, researcher_name, sponsoring_company]):
            return Research.objects.none()

        if title:
            queryset = queryset.filter(title__icontains=title)

        if description:
            queryset = queryset.filter(description__icontains=description)

        if status:
            queryset = queryset.filter(status__iexact=status)

        if knowledge_area:
            queryset = queryset.filter(knowledge_area__icontains=knowledge_area)

        print(f"Buscando empresa: '{sponsoring_company}'")
        
        if sponsoring_company:
            queryset = queryset.filter(sponsoring_company__fantasyName__icontains=sponsoring_company)

        if keywords:
            kw_filter = Q()
            for kw in keywords:
                kw_filter |= Q(keywords__contains=[kw])
            queryset = queryset.filter(kw_filter)

        if campus:
            queryset = queryset.filter(campus__iexact=campus)

        if researcher_name:
            terms = researcher_name.split()

            q = Q()
            for term in terms:
                q &= (
                    Q(members__researcher_profile__firstName__icontains=term) |
                    Q(members__researcher_profile__surname__icontains=term) |
                    Q(members__collaborator_profile__firstName__icontains=term) |
                    Q(members__collaborator_profile__surname__icontains=term)
                )

            queryset = queryset.filter(q).distinct()

        return queryset