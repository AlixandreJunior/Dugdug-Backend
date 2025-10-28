from django.urls import path

from apps.plan import views

app_name = "plan"

urlpatterns = [
    path("list/", views.PlanListView.as_view(), name="list"),
    path("create/", views.PlanCreateView.as_view(), name="create"),
    path("detail/<str:name>/", views.PlanDetailView.as_view(), name="detail"),
    path("update/<str:name>/", views.PlanUpdateView.as_view(), name="update"),
    path("delete/<str:name>/", views.PlanDeleteView.as_view(), name="delete"),
    path(
        "subscriptions/", views.SubscriptionListView.as_view(), name="subscription-list"
    ),
    path(
        "subscriptions/create/",
        views.SubscriptionCreateView.as_view(),
        name="subscription-create",
    ),
    path(
        "subscriptions/<int:pk>/",
        views.SubscriptionDetailView.as_view(),
        name="subscription-detail",
    ),
    path(
        "subscriptions/<int:pk>/cancel/",
        views.SubscriptionCancelView.as_view(),
        name="subscription-cancel",
    ),
    # --------------------------
    # ADMIN
    # --------------------------
    path(
        "subscriptions/admin/",
        views.SubscriptionAdminListView.as_view(),
        name="subscription-admin-list",
    ),
]
