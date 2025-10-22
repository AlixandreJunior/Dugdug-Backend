from django.urls import path

from apps.affiliate.views import (
    AffiliateCreateView,
    AffiliateDeleteView,
    AffiliateDetailView,
    AffiliateListView,
    AffiliateUpdateView,
    PayoutCreateView,
    PayoutDeleteView,
    PayoutDetailView,
    PayoutListView,
    PayoutUpdateView,
)

urlpatterns = [
    # Affiliate
    path("affiliates/create/", AffiliateCreateView.as_view(), name="affiliate-create"),
    path("affiliates/", AffiliateListView.as_view(), name="affiliate-list"),
    path(
        "affiliates/<int:pk>/", AffiliateDetailView.as_view(), name="affiliate-detail"
    ),
    path(
        "affiliates/<int:pk>/update/",
        AffiliateUpdateView.as_view(),
        name="affiliate-update",
    ),
    path(
        "affiliates/<int:pk>/delete/",
        AffiliateDeleteView.as_view(),
        name="affiliate-delete",
    ),
    # Payout
    path("payouts/create/", PayoutCreateView.as_view(), name="payout-create"),
    path("payouts/", PayoutListView.as_view(), name="payout-list"),
    path("payouts/<int:pk>/", PayoutDetailView.as_view(), name="payout-detail"),
    path("payouts/<int:pk>/update/", PayoutUpdateView.as_view(), name="payout-update"),
    path("payouts/<int:pk>/delete/", PayoutDeleteView.as_view(), name="payout-delete"),
]
