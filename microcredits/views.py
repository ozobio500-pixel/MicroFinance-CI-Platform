from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgent, IsClient
from notifications.services import notify_user

from .models import CreditApplication, CreditDocument
from .serializers import (
    CreditApplicationCreateSerializer,
    CreditApplicationSerializer,
    CreditDocumentSerializer,
    CreditStatusUpdateSerializer,
)
from .services import compute_eligibility_score, generate_repayment_schedule


class CreditApplicationListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsClient()]
        if self.request.user.is_authenticated and self.request.user.is_client:
            return [IsClient()]
        return [IsAgent()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreditApplicationCreateSerializer
        return CreditApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = CreditApplication.objects.select_related("client", "assigned_agent").prefetch_related(
            "documents"
        )
        if user.is_client:
            return qs.filter(client=user)
        return qs

    def perform_create(self, serializer):
        score = compute_eligibility_score(self.request.user, serializer.validated_data["amount"])
        serializer.save(
            client=self.request.user,
            eligibility_score=score,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = CreditApplicationSerializer(serializer.instance, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CreditApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = CreditApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = CreditApplication.objects.prefetch_related("documents")
        if user.is_client:
            return qs.filter(client=user)
        return qs


class CreditStatusUpdateView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(request=CreditStatusUpdateSerializer, responses=CreditApplicationSerializer)
    def patch(self, request, pk):
        try:
            app = CreditApplication.objects.get(pk=pk)
        except CreditApplication.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreditStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]

        transitions = {
            CreditApplication.Status.SUBMITTED: [CreditApplication.Status.IN_REVIEW],
            CreditApplication.Status.IN_REVIEW: [CreditApplication.Status.APPROVED],
            CreditApplication.Status.APPROVED: [CreditApplication.Status.DISBURSED],
        }
        allowed = transitions.get(app.status, [])
        if new_status not in allowed:
            return Response(
                {"detail": f"Transition {app.status} → {new_status} non autorisée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        app.status = new_status
        if request.user.is_agent and not app.assigned_agent_id:
            app.assigned_agent = request.user

        if new_status == CreditApplication.Status.DISBURSED:
            app.disbursed_at = timezone.now()
            from repayments.models import RepaymentInstallment

            RepaymentInstallment.objects.bulk_create(generate_repayment_schedule(app))

        app.save()
        notify_user(
            app.client,
            "Mise à jour de votre crédit",
            f"Statut : {app.get_status_display()}.",
            "credit_status",
        )
        return Response(CreditApplicationSerializer(app).data)


class CreditDocumentUploadView(generics.CreateAPIView):
    serializer_class = CreditDocumentSerializer
    permission_classes = [IsClient]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        app = CreditApplication.objects.get(pk=self.kwargs["pk"], client=self.request.user)
        serializer.save(application=app)
