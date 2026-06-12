from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'title',
        'category',
        'is_read',
        'created_at',
    ]
    list_filter = ['is_read', 'category']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    raw_id_fields = ['user']
