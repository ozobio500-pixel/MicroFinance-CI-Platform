from django.urls import path

from .views import (
    CreditApplicationDetailView,
    CreditApplicationListCreateView,
    CreditDocumentUploadView,
    CreditStatusUpdateView,
)

urlpatterns = [
    path("applications/", CreditApplicationListCreateView.as_view(), name="credit-list"),
    path("applications/<int:pk>/", CreditApplicationDetailView.as_view(), name="credit-detail"),
    path(
        "applications/<int:pk>/status/",
        CreditStatusUpdateView.as_view(),
        name="credit-status",
    ),
    path(
        "applications/<int:pk>/documents/",
        CreditDocumentUploadView.as_view(),
        name="credit-documents",
    ),
]
