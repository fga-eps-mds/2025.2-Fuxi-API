from django.urls import path
from .views import (
    ResearcherListCreateView, ResearcherDetailView,
    CollaboratorListCreateView, CollaboratorDetailView,
    CompanyListCreateView, CompanyDetailView
)

urlpatterns = [
    path('researchers/', ResearcherListCreateView.as_view(), name='researcher-list-create'),
    path('researchers/<int:pk>/', ResearcherDetailView.as_view(), name='researcher-detail'),

    path('collaborators/', CollaboratorListCreateView.as_view(), name='collaborator-list-create'),
    path('collaborators/<int:pk>/', CollaboratorDetailView.as_view(), name='collaborator-detail'),
    
    path('companies/', CompanyListCreateView.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
]
