from django.contrib import admin

from .models import Affiliate, Payout


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin[Affiliate]):
    list_display = (
        "user",
        "code",
        "commission_balance",
        "total_earned",
        "pix_key_type",
        "joined_at",
    )
    list_filter = ("pix_key_type", "joined_at")
    search_fields = ("user__username", "user__email", "code", "pix_key")
    readonly_fields = ("joined_at",)
    fieldsets = (
        (
            "Informações do Afiliado",
            {
                "fields": ("user", "code", "joined_at"),
            },
        ),
        (
            "Financeiro",
            {
                "fields": ("commission_balance", "total_earned"),
            },
        ),
        (
            "Dados Pix",
            {
                "fields": ("pix_key_type", "pix_key"),
            },
        ),
    )

    def get_ordering(self, request: object) -> tuple[str]:
        return ("-joined_at",)


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin[Payout]):
    list_display = (
        "affiliate",
        "amount",
        "status",
        "requested_at",
        "paid_at",
    )
    list_filter = ("status", "requested_at", "paid_at")
    search_fields = ("affiliate__user__username", "affiliate__user__email", "status")
    readonly_fields = ("requested_at",)
    fieldsets = (
        (
            "Informações de Pagamento",
            {
                "fields": ("affiliate", "amount", "pix_key", "status"),
            },
        ),
        (
            "Datas",
            {
                "fields": ("requested_at", "paid_at"),
            },
        ),
        (
            "Outros",
            {
                "fields": ("notes",),
            },
        ),
    )

    def get_ordering(self, request: object) -> tuple[str]:
        return ("-requested_at",)
