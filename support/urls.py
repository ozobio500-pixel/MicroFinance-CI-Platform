from django.urls import path

from .views import AssignConversationView, ConversationDetailView, ConversationListCreateView

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list"),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path(
        "conversations/<int:pk>/assign/",
        AssignConversationView.as_view(),
        name="conversation-assign",
    ),
]
