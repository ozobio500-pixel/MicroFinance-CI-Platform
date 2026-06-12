from django.conf import settings
from django.db import models


class Conversation(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Ouverte"
        ASSIGNED = "assigned", "Assignée"
        CLOSED = "closed", "Fermée"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_conversations",
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_conversations",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    subject = models.CharField(max_length=200, blank=True, default="Support COFINANCE CI")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
