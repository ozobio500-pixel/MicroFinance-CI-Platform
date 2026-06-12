from rest_framework import serializers

from .models import RepaymentInstallment


class RepaymentInstallmentSerializer(serializers.ModelSerializer):
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)

    class Meta:
        model = RepaymentInstallment
        fields = (
            "id",
            "application",
            "installment_number",
            "due_date",
            "principal_amount",
            "interest_amount",
            "penalty_amount",
            "total_due",
            "amount_paid",
            "balance_due",
            "status",
            "paid_at",
        )
        read_only_fields = fields


class RecordPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=0, min_value=1)
