from rest_framework import serializers


class DashboardFiltersSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    region = serializers.CharField(required=False, allow_null=True)
    agent = serializers.IntegerField(required=False, allow_null=True)


class DashboardKPISerializer(serializers.Serializer):
    generated_at = serializers.DateTimeField()
    credits_by_status = serializers.DictField(child=serializers.IntegerField())
    total_credit_requests = serializers.IntegerField()
    recovery_rate_percent = serializers.FloatField()
    active_insurance_subscriptions = serializers.IntegerField()
    open_support_conversations = serializers.IntegerField()
    filters_applied = DashboardFiltersSerializer()
