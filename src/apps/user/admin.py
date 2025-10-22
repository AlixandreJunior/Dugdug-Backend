from django.contrib import admin

from apps.user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore
    model = User
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "cpf",
        "phone",
        "is_active",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email", "cpf", "phone")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "cpf", "phone")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
