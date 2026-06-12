from django.contrib import admin

from .models import RepaymentInstallment


@admin.register(RepaymentInstallment)
class RepaymentInstallmentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'application',
        'installment_number',
        'due_date',
        'total_due',
        'amount_paid',
        'status',
        'paid_at',
    ]
    list_filter = ['status']
    search_fields = [
        'application__client__username',
        'application__client__email',
    ]
    raw_id_fields = ['application', 'recorded_by']
