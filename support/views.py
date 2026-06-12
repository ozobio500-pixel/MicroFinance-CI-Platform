from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminRole, IsClient

from .models import Conversation
from .serializers import ConversationCreateSerializer, ConversationSerializer

User = get_user_model()


class ConversationListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsClient()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Conversation.objects.select_related("client", "assigned_agent").prefetch_related(
            "messages__sender"
        )
        if user.is_client:
            return qs.filter(client=user)
        return qs

    def perform_create(self, serializer):
        conv = serializer.save(client=self.request.user)
        agent = User.objects.filter(role=User.Role.ADMIN, is_active=True).order_by("id").first()
        if agent:
            conv.assigned_agent = agent
            conv.status = Conversation.Status.ASSIGNED
            conv.save(update_fields=["assigned_agent", "status"])


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Conversation.objects.prefetch_related("messages__sender")
        if user.is_client:
            return qs.filter(client=user)
        return qs


class AssignConversationView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            conv = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        conv.assigned_agent = request.user
        conv.status = Conversation.Status.ASSIGNED
        conv.save()
        return Response(ConversationSerializer(conv).data)
