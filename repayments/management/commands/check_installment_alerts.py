from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications.services import notify_user
from repayments.models import RepaymentInstallment


class Command(BaseCommand):
    help = "Alertes J-3 et J+1 pour les échéances de remboursement."

    def handle(self, *args, **options):
        today = timezone.now().date()
        j3 = today + timedelta(days=3)
        j1_late = today - timedelta(days=1)

        upcoming = RepaymentInstallment.objects.filter(
            status=RepaymentInstallment.Status.PENDING,
            due_date=j3,
        ).select_related("application__client")

        for inst in upcoming:
            client = inst.application.client
            notify_user(
                client,
                "Échéance dans 3 jours",
                f"Échéance #{inst.installment_number} de {inst.total_due} FCFA le {inst.due_date}.",
                "installment_reminder_j3",
            )

        late = RepaymentInstallment.objects.filter(
            status__in=[
                RepaymentInstallment.Status.PENDING,
                RepaymentInstallment.Status.LATE,
            ],
            due_date=j1_late,
        ).select_related("application__client")

        for inst in late:
            inst.apply_penalty_if_late()
            client = inst.application.client
            notify_user(
                client,
                "Échéance en retard",
                f"L'échéance #{inst.installment_number} est en retard. Pénalités applicables.",
                "installment_late_j1",
            )

        self.stdout.write(self.style.SUCCESS("Alertes échéances traitées."))
