from django.contrib import admin

from .models import InsuranceProduct, InsuranceSubscription


@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'product_type',
        'premium_monthly',
        'coverage_amount',
        'duration_months',
        'is_active',
    ]
    list_filter = ['product_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(InsuranceSubscription)
class InsuranceSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client',
        'product',
        'policy_number',
        'status',
        'start_date',
        'end_date',
        'created_at',
    ]
    list_filter = ['status', 'product']
    search_fields = ['client__username', 'client__email', 'policy_number']
    raw_id_fields = ['client', 'product']
