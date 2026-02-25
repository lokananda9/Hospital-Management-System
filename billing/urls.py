from django.urls import path

from .views import InvoiceListCreateView, InvoiceStatusUpdateView

urlpatterns = [
    path("invoices/", InvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("invoices/<int:pk>/status/", InvoiceStatusUpdateView.as_view(), name="invoice-status-update"),
]
