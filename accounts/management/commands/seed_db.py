from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from insurance.models import InsuranceProduct, InsuranceSubscription
from microcredits.models import CreditApplication
from repayments.models import RepaymentInstallment
from support.models import Conversation, Message

User = get_user_model()


class Command(BaseCommand):
    help = "Jeu de données de démonstration (cahier des charges §7)."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cofinance.ci",
                "first_name": "Aminata",
                "last_name": "Koné",
                "role": User.Role.ADMIN,
                "region": User.Region.ABIDJAN,
            },
        )
        admin.set_password("demo1234")
        admin.save()

        agent, _ = User.objects.get_or_create(
            username="agent1",
            defaults={
                "role": User.Role.AGENT,
                "region": User.Region.BOUAKE,
                "credit_score": 50,
            },
        )
        agent.set_password("demo1234")
        agent.save()

        client1, _ = User.objects.get_or_create(
            username="client1",
            defaults={
                "role": User.Role.CLIENT,
                "region": User.Region.ABIDJAN,
                "credit_score": 72,
            },
        )
        client1.set_password("demo1234")
        client1.save()

        life, _ = InsuranceProduct.objects.get_or_create(
            name="Vie Essentielle",
            defaults={
                "product_type": InsuranceProduct.ProductType.LIFE,
                "premium_monthly": 2500,
                "coverage_amount": 500_000,
            },
        )
        InsuranceProduct.objects.get_or_create(
            name="Protection Famille",
            defaults={
                "product_type": InsuranceProduct.ProductType.DEATH_DISABILITY,
                "premium_monthly": 3500,
                "coverage_amount": 1_000_000,
            },
        )

        InsuranceSubscription.objects.get_or_create(
            policy_number="COF-00001-0001",
            defaults={
                "client": client1,
                "product": life,
                "start_date": date.today() - timedelta(days=60),
                "end_date": date.today() + timedelta(days=305),
            },
        )

        app1, _ = CreditApplication.objects.get_or_create(
            client=client1,
            amount=350_000,
            defaults={
                "duration_months": 6,
                "status": CreditApplication.Status.DISBURSED,
                "eligibility_score": 68,
                "assigned_agent": agent,
                "disbursed_at": timezone.now() - timedelta(days=30),
            },
        )
        if not app1.installments.exists():
            RepaymentInstallment.objects.create(
                application=app1,
                installment_number=1,
                due_date=date.today() + timedelta(days=15),
                principal_amount=Decimal("55000"),
                interest_amount=Decimal("3500"),
                total_due=Decimal("58500"),
            )

        CreditApplication.objects.get_or_create(
            client=client1,
            amount=200_000,
            defaults={
                "status": CreditApplication.Status.SUBMITTED,
                "eligibility_score": 65,
            },
        )

        conv, _ = Conversation.objects.get_or_create(
            client=client1,
            subject="Support remboursement",
            defaults={"assigned_agent": admin, "status": Conversation.Status.ASSIGNED},
        )
        if not conv.messages.exists():
            Message.objects.create(conversation=conv, sender=client1, content="Bonjour.")
            Message.objects.create(conversation=conv, sender=admin, content="Bonjour, comment puis-je vous aider ?")

        self.stdout.write(self.style.SUCCESS("seed_db terminé (admin, agent1, client1 / demo1234)."))
