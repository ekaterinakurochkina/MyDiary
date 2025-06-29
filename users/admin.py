from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class DiaryAdmin(UserAdmin):
    list_display = ('id', 'email', 'display_name', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('id', 'email', 'is_active',)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )
    ordering = ('pk',)
    readonly_fields = ("last_login", "date_joined")
