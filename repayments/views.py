from decimal import Decimal

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgent, IsClient
from notifications.services import notify_user

from .models import RepaymentInstallment
from .serializers import RecordPaymentSerializer, RepaymentInstallmentSerializer


class InstallmentListView(generics.ListAPIView):
    serializer_class = RepaymentInstallmentSerializer
    permission_classes = [IsAgent]

    def get_queryset(self):
        qs = RepaymentInstallment.objects.select_related("application", "application__client")
        application_id = self.request.query_params.get("application")
        if application_id:
            qs = qs.filter(application_id=application_id)
        for inst in qs:
            inst.apply_penalty_if_late()
        return qs


class RecordPaymentView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(request=RecordPaymentSerializer, responses=RepaymentInstallmentSerializer)
    def post(self, request, pk):
        try:
            installment = RepaymentInstallment.objects.select_related(
                "application__client"
            ).get(pk=pk)
        except RepaymentInstallment.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]
        installment.apply_penalty_if_late()

        installment.amount_paid += Decimal(amount)
        if installment.amount_paid >= installment.total_due + installment.penalty_amount:
            installment.status = RepaymentInstallment.Status.PAID
            installment.paid_at = timezone.now()
            installment.recorded_by = request.user
        installment.save()

        notify_user(
            installment.application.client,
            "Remboursement enregistré",
            f"Échéance #{installment.installment_number} : {amount} FCFA.",
            "repayment_recorded",
        )
        return Response(RepaymentInstallmentSerializer(installment).data)


class ClientRepaymentHistoryView(generics.ListAPIView):
    serializer_class = RepaymentInstallmentSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        qs = RepaymentInstallment.objects.filter(
            application__client=self.request.user
        ).select_related("application")
        for inst in qs:
            inst.apply_penalty_if_late()
        return qs
