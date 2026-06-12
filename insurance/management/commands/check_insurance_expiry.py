from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from insurance.models import InsuranceSubscription
from notifications.services import notify_user


class Command(BaseCommand):
    help = "Notification 15 jours avant expiration des polices."

    def handle(self, *args, **options):
        target = timezone.now().date() + timedelta(days=15)
        subs = InsuranceSubscription.objects.filter(
            status=InsuranceSubscription.Status.ACTIVE,
            end_date=target,
        ).select_related("client", "product")

        for sub in subs:
            notify_user(
                sub.client,
                "Renouvellement assurance",
                f"Votre police {sub.policy_number} ({sub.product.name}) expire le {sub.end_date}.",
                "insurance_expiry_15d",
            )

        self.stdout.write(self.style.SUCCESS(f"{subs.count()} notification(s) envoyée(s)."))
