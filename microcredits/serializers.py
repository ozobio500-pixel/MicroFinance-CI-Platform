from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import CreditApplication, CreditDocument


class CreditDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditDocument
        fields = ("id", "file", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class CreditApplicationSerializer(serializers.ModelSerializer):
    client_detail = UserSerializer(source="client", read_only=True)
    documents = CreditDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = CreditApplication
        fields = (
            "id",
            "client",
            "client_detail",
            "amount",
            "duration_months",
            "status",
            "eligibility_score",
            "assigned_agent",
            "documents",
            "created_at",
            "updated_at",
            "disbursed_at",
        )
        read_only_fields = fields


class CreditApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditApplication
        fields = ("id", "amount", "duration_months", "status", "eligibility_score", "created_at")
        read_only_fields = ("id", "status", "eligibility_score", "created_at")


class CreditStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CreditApplication.Status.choices)
