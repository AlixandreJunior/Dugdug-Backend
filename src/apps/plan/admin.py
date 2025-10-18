from django.contrib import admin
from django.http import HttpRequest

from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin[Plan]):
    list_display = ("name", "price", "duration_days")
    search_fields = ("name",)
    ordering = ("price",)
    list_editable = ("price", "duration_days")
    list_per_page = 20


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin[Subscription]):
    list_display = (
        "costumer",
        "plan",
        "affiliate",
        "start_date",
        "end_date",
        "is_active",
        "payment_method",
    )
    list_filter = ("is_active", "payment_method", "start_date")
    search_fields = ("costumer__username", "plan__name", "affiliate__user__username")
    ordering = ("-start_date",)
    autocomplete_fields = ("costumer", "plan", "affiliate")
    list_per_page = 20

    def get_ordering(self, request: HttpRequest) -> tuple[str]:
        return ("-start_date",)

    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return request.user.is_superuser
