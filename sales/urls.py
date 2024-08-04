from django.urls import path
from .views import (
    DailyAnalyticsView,
    ExportInvoicesToExcel,
    MonthlyTrafficSalesView,
    TransactionListCreateAPIView,
    TransactionDetailAPIView,
    InvoiceListCreateAPIView,
    InvoiceDetailAPIView,
    WeeklyActiveUsersView,
)

urlpatterns = [
    path(
        "transactions/",
        TransactionListCreateAPIView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "transactions/<uuid:pk>/",
        TransactionDetailAPIView.as_view(),
        name="transaction-detail",
    ),
    path("invoices/", InvoiceListCreateAPIView.as_view(), name="invoice-list-create"),
    path("invoices/<uuid:pk>/", InvoiceDetailAPIView.as_view(), name="invoice-detail"),
    path("analytics/daily/", DailyAnalyticsView.as_view(), name="daily-analytics"),
    path(
        "weekly-active-users/",
        WeeklyActiveUsersView.as_view(),
        name="weekly-active-users",
    ),
    path(
        "monthly-traffic-sales/",
        MonthlyTrafficSalesView.as_view(),
        name="monthly-traffic-sales",
    ),
    path(
        "export-invoices/",
        ExportInvoicesToExcel.as_view(),
        name="export_invoices_to_excel",
    ),
]
