from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdminRole
from insurance.models import InsuranceSubscription
from microcredits.models import CreditApplication
from repayments.models import RepaymentInstallment
from support.models import Conversation
from .serializers import DashboardKPISerializer


def get_agent_choices():
    try:
        # Récupère dynamiquement les IDs des admins et des agents de terrain
        ids = list(User.objects.filter(role__in=[User.Role.ADMIN, User.Role.AGENT]).values_list("id", flat=True))
        return ids if ids else [1, 2]
    except Exception:
        return [1, 2]


class DashboardKPIView(APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(
        parameters=[
            OpenApiParameter("date_from", type=OpenApiTypes.DATE, description="Date de début (YYYY-MM-DD)"),
            OpenApiParameter("date_to", type=OpenApiTypes.DATE, description="Date de fin (YYYY-MM-DD)"),
            OpenApiParameter(
                "region",
                type=OpenApiTypes.STR,
                enum=User.Region.values,
                description="Région du client",
            ),
            OpenApiParameter(
                "agent",
                type=OpenApiTypes.INT,
                enum=get_agent_choices(),
                description="ID de l'agent de terrain",
            ),
        ],
        responses={200: DashboardKPISerializer},
        description="Indicateurs clés : crédits, recouvrement, assurances, support.",
    )
    def get(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        region = request.query_params.get("region")
        agent_id = request.query_params.get("agent")

        credits = CreditApplication.objects.all()
        installments = RepaymentInstallment.objects.all()
        conversations = Conversation.objects.all()

        if date_from:
            credits = credits.filter(created_at__date__gte=date_from)
            installments = installments.filter(due_date__gte=date_from)
        if date_to:
            credits = credits.filter(created_at__date__lte=date_to)
            installments = installments.filter(due_date__lte=date_to)
        if region:
            credits = credits.filter(client__region=region)
        if agent_id:
            credits = credits.filter(assigned_agent_id=agent_id)
            conversations = conversations.filter(assigned_agent_id=agent_id)

        credits_by_status = dict(
            credits.values("status").annotate(count=Count("id")).values_list("status", "count")
        )

        total_due = installments.exclude(status=RepaymentInstallment.Status.PAID).aggregate(
            s=Sum("total_due")
        )["s"] or Decimal(0)
        total_paid = installments.filter(status=RepaymentInstallment.Status.PAID).aggregate(
            s=Sum("amount_paid")
        )["s"] or Decimal(0)
        recovery_rate = float(total_paid / (total_paid + total_due) * 100) if (total_paid + total_due) else 0

        active_insurance = InsuranceSubscription.objects.filter(
            status=InsuranceSubscription.Status.ACTIVE
        ).count()

        open_chats = conversations.filter(status=Conversation.Status.OPEN).count()

        return Response(
            {
                "generated_at": timezone.now().isoformat(),
                "credits_by_status": credits_by_status,
                "total_credit_requests": credits.count(),
                "recovery_rate_percent": round(recovery_rate, 2),
                "active_insurance_subscriptions": active_insurance,
                "open_support_conversations": open_chats,
                "filters_applied": {
                    "date_from": date_from,
                    "date_to": date_to,
                    "region": region,
                    "agent": agent_id,
                },
            }
        )
