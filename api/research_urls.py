from django.urls import path
from .research_views import (
  ResearchListCreateView, ResearchListPublicView, ResearchDetailView, ResearchDetailPublicView
)

urlpatterns = [
    path("", ResearchListCreateView.as_view(), name="research-list-create"),
    path("<int:pk>/", ResearchDetailView.as_view(), name="research-detail"),
    path("all/", ResearchListPublicView.as_view(), name="research-public-list"),
    path("all/<int:pk>", ResearchDetailPublicView.as_view(), name="research-public-list-detail"),
]