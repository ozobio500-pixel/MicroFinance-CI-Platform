from django.conf import settings
from django.db import models


class CreditApplication(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Soumise"
        IN_REVIEW = "in_review", "En analyse"
        APPROVED = "approved", "Approuvée"
        DISBURSED = "disbursed", "Décaissée"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credit_applications",
    )
    amount = models.PositiveIntegerField(help_text="Montant demandé en FCFA")
    duration_months = models.PositiveSmallIntegerField(default=6)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    eligibility_score = models.PositiveSmallIntegerField(null=True, blank=True)
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_credits",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class CreditDocument(models.Model):
    application = models.ForeignKey(
        CreditApplication,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    file = models.FileField(upload_to="credit_documents/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
