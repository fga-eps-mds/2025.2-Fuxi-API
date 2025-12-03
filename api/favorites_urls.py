from django.urls import path
from .favorites_views import (
    FavoriteResearchListView, FavoriteResearchCreateView, FavoriteResearchDeleteView
)

urlpatterns = [
    path("add/", FavoriteResearchCreateView.as_view(), name="favorite-add"),
    path("remove/<int:pk>", FavoriteResearchDeleteView.as_view(), name="favorite-remove"),
    path("", FavoriteResearchListView.as_view(), name="favorite-list"),
]