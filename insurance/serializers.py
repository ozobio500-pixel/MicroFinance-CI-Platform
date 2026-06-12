from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import InsuranceProduct, InsuranceSubscription


class InsuranceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProduct
        fields = (
            "id",
            "name",
            "product_type",
            "description",
            "premium_monthly",
            "coverage_amount",
            "duration_months",
            "is_active",
        )


class InsuranceSubscriptionSerializer(serializers.ModelSerializer):
    product_detail = InsuranceProductSerializer(source="product", read_only=True)

    class Meta:
        model = InsuranceSubscription
        fields = (
            "id",
            "client",
            "product",
            "product_detail",
            "policy_number",
            "start_date",
            "end_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "client", "policy_number", "start_date", "end_date", "status", "created_at")


class SubscribeSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def create_subscription(self, client):
        product = InsuranceProduct.objects.get(pk=self.validated_data["product_id"], is_active=True)
        start = timezone.now().date()
        end = start + timedelta(days=product.duration_months * 30)
        policy_number = f"COF-{client.id:05d}-{InsuranceSubscription.objects.count() + 1:04d}"
        return InsuranceSubscription.objects.create(
            client=client,
            product=product,
            policy_number=policy_number,
            start_date=start,
            end_date=end,
        )
