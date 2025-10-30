from django.shortcuts import render
from rest_framework import generics, status
from django.contrib.auth.hashers import make_password
from .models import Researcher, Collaborator, Company
from .serializers import ResearcherSerializer, CollaboratorSerializer, CompanySerializer

class ResearcherListCreateView(generics.ListCreateAPIView):
    queryset = Researcher.objects.all()
    serializer_class = ResearcherSerializer

    def perform_create(self, serializer):
        password = serializer.validated_data['password']
        serializer.save(password=make_password(password))


class ResearcherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Researcher.objects.all()
    serializer_class = ResearcherSerializer

    def perform_update(self, serializer):
        if 'password' in serializer.validated_data:
            password = serializer.validated_data['password']
            serializer.validated_data['password'] = make_password(password)
        serializer.save()

class CollaboratorListCreateView(generics.ListCreateAPIView):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer

    def perform_create(self, serializer):
        password = serializer.validated_data['password']
        serializer.save(password=make_password(password))


class CollaboratorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer

    def perform_update(self, serializer):
        if 'password' in serializer.validated_data:
            password = serializer.validated_data['password']
            serializer.validated_data['password'] = make_password(password)
        serializer.save()

class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def perform_create(self, serializer):
        password = serializer.validated_data['password']
        serializer.save(password=make_password(password))


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def perform_update(self, serializer):
        if 'password' in serializer.validated_data:
            password = serializer.validated_data['password']
            serializer.validated_data['password'] = make_password(password)
        serializer.save()