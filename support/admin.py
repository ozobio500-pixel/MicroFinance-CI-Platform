from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'subject',
        'client',
        'assigned_agent',
        'status',
        'updated_at',
    ]
    list_filter = ['status']
    search_fields = [
        'subject',
        'client__username',
        'assigned_agent__username',
    ]
    raw_id_fields = ['client', 'assigned_agent']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'created_at']
    search_fields = ['content', 'sender__username']
    raw_id_fields = ['conversation', 'sender']
