from django.conf import settings
from django.db import models
from django.utils import timezone


class InsuranceProduct(models.Model):
    class ProductType(models.TextChoices):
        LIFE = "life", "Assurance vie simplifiée"
        DEATH_DISABILITY = "death_disability", "Décès-invalidité"

    name = models.CharField(max_length=150)
    product_type = models.CharField(max_length=30, choices=ProductType.choices)
    description = models.TextField(blank=True)
    premium_monthly = models.PositiveIntegerField()
    coverage_amount = models.PositiveIntegerField()
    duration_months = models.PositiveSmallIntegerField(default=12)
    is_active = models.BooleanField(default=True)


class InsuranceSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expirée"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="insurance_subscriptions",
    )
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT, related_name="subscriptions")
    policy_number = models.CharField(max_length=30, unique=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
