from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class RepaymentInstallment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "À payer"
        PAID = "paid", "Payée"
        LATE = "late", "En retard"

    application = models.ForeignKey(
        "microcredits.CreditApplication",
        on_delete=models.CASCADE,
        related_name="installments",
    )
    installment_number = models.PositiveSmallIntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=12, decimal_places=0)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=0)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_due = models.DecimalField(max_digits=12, decimal_places=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )

    class Meta:
        ordering = ["application", "installment_number"]
        unique_together = [("application", "installment_number")]

    @property
    def balance_due(self) -> Decimal:
        return self.total_due + self.penalty_amount - self.amount_paid

    def apply_penalty_if_late(self):
        from django.conf import settings as django_settings

        if self.status == self.Status.PAID:
            return
        if timezone.now().date() > self.due_date:
            self.status = self.Status.LATE
            rate = Decimal(str(django_settings.CREDIT_PENALTY_RATE))
            self.penalty_amount = (self.total_due * rate).quantize(Decimal("1"))
            self.save(update_fields=["status", "penalty_amount"])
