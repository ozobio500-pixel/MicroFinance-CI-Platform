import calendar
from datetime import date
from decimal import Decimal

from django.conf import settings


def _add_months(start: date, months: int) -> date:
    y = start.year + (start.month - 1 + months) // 12
    m = (start.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(y, m)[1]
    return date(y, m, min(start.day, last_day))


def compute_eligibility_score(client, amount: int) -> int:
    """Score simplifié 0-100 basé sur le profil client."""
    score = client.credit_score
    if amount > 1_000_000:
        score -= 15
    elif amount > 500_000:
        score -= 5
    from microcredits.models import CreditApplication

    active = CreditApplication.objects.filter(
        client=client,
        status__in=[CreditApplication.Status.APPROVED, CreditApplication.Status.DISBURSED],
    ).count()
    score -= active * 10
    return max(0, min(100, score))


def generate_repayment_schedule(application):
    """Génère l'échéancier mensuel après décaissement."""
    from repayments.models import RepaymentInstallment

    principal = Decimal(application.amount)
    n = application.duration_months
    annual_rate = Decimal(str(settings.CREDIT_DEFAULT_RATE))
    monthly_rate = annual_rate / Decimal("12")
    if monthly_rate > 0:
        payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -n)
        payment = payment.quantize(Decimal("1"))
    else:
        payment = (principal / n).quantize(Decimal("1"))

    balance = principal
    installments = []
    due = _add_months(date.today(), 1)

    for i in range(1, n + 1):
        interest = (balance * monthly_rate).quantize(Decimal("1"))
        principal_part = payment - interest
        if i == n:
            principal_part = balance
            payment = principal_part + interest
        balance -= principal_part
        installments.append(
            RepaymentInstallment(
                application=application,
                installment_number=i,
                due_date=due,
                principal_amount=principal_part,
                interest_amount=interest,
                total_due=payment,
            )
        )
        due = _add_months(due, 1)

    return installments
