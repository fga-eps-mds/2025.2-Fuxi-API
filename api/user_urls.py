from django.urls import path
from .user_views import (
    ResearcherListCreateView, ResearcherDetailView,
    CollaboratorListCreateView, CollaboratorDetailView,
    CompanyListCreateView, CompanyDetailView, LoginView, ProfileView, UserCreateView, UserListView, UserDetailView, LogoutView
)

urlpatterns = [
    path("", UserListView.as_view(), name="users-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="users-detail"),

    path("register/", UserCreateView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path("logout/", LogoutView.as_view(), name="user-logout"),

    path('researchers/', ResearcherListCreateView.as_view(), name='researcher-list-create'),
    path('researchers/<int:pk>/', ResearcherDetailView.as_view(), name='researcher-detail'),

    path('collaborators/', CollaboratorListCreateView.as_view(), name='collaborator-list-create'),
    path('collaborators/<int:pk>/', CollaboratorDetailView.as_view(), name='collaborator-detail'),
    
    path('companies/', CompanyListCreateView.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
]
