from django.contrib import admin

from .models import CreditApplication, CreditDocument


@admin.register(CreditApplication)
class CreditApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client',
        'amount',
        'duration_months',
        'status',
        'assigned_agent',
        'created_at',
    ]
    list_filter = ['status', 'duration_months', 'assigned_agent']
    search_fields = [
        'client__username',
        'client__email',
        'assigned_agent__username',
    ]
    raw_id_fields = ['client', 'assigned_agent']


@admin.register(CreditDocument)
class CreditDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'file', 'uploaded_at']
    list_filter = ['uploaded_at']
    raw_id_fields = ['application']
