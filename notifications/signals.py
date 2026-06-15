from django.db.models.signals import post_save
from django.dispatch import receiver

from microcredits.models import CreditApplication
from repayments.models import RepaymentInstallment
from insurance.models import InsuranceSubscription
from support.models import Conversation

from .services import notify_user


@receiver(post_save, sender=CreditApplication)
def notify_credit_status_change(sender, instance, created, **kwargs):
    if created:
        return
    messages = {
        "analyzing": ("Dossier en analyse", "Votre demande de credit est en cours d analyse."),
        "approved": ("Credit approuve", "Felicitations, votre demande de credit a ete approuvee."),
        "disbursed": ("Credit decaisse", "Votre credit a ete decaisse avec succes."),
        "rejected": ("Demande rejetee", "Votre demande de credit n a pas pu etre approuvee."),
    }
    if instance.status in messages:
        title, message = messages[instance.status]
        notify_user(instance.client, title, message, category="credit")


@receiver(post_save, sender=RepaymentInstallment)
def notify_repayment_recorded(sender, instance, created, **kwargs):
    if instance.status == RepaymentInstallment.Status.PAID:
        notify_user(
            instance.application.client,
            "Remboursement enregistre",
            f"Votre paiement de {instance.amount_paid} FCFA a bien ete enregistre.",
            category="repayment",
        )


@receiver(post_save, sender=InsuranceSubscription)
def notify_insurance_confirmed(sender, instance, created, **kwargs):
    if created:
        notify_user(
            instance.client,
            "Souscription confirmee",
            f"Votre souscription au produit {instance.product.name} est active.",
            category="insurance",
        )


@receiver(post_save, sender=Conversation)
def notify_agent_new_conversation(sender, instance, created, **kwargs):
    """Notifie l agent assigne quand une nouvelle conversation est creee (CDC section 5.1)."""
    if not created:
        return
    if not instance.assigned_agent:
        return
    notify_user(
        instance.assigned_agent,
        "Nouvelle conversation de support",
        f"Le client {instance.client.username} a ouvert une nouvelle conversation : {instance.subject or 'Support'}.",
        category="support",
    )