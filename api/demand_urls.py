from django.urls import path
from .demand_views import (
  DemandListCreateView, DemandListPublicView, DemandDetailView, DemandDetailPublicView, DemandSearchView
)

urlpatterns = [
    path("", DemandListCreateView.as_view(), name="demand-list-create"),
    path("<int:pk>/", DemandDetailView.as_view(), name="demand-detail"),
    path("all/", DemandListPublicView.as_view(), name="demand-public-list"),
    path("all/<int:pk>", DemandDetailPublicView.as_view(), name="demand-public-list-detail"),
    path("search/", DemandSearchView.as_view(), name="demand-search"),
]