from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'is_superuser',
    ]
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (
            'Informations supplémentaires',
            {
                'fields': ('role', 'phone', 'region', 'credit_score'),
            },
        ),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']
