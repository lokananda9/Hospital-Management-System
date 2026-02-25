from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Invoice
from .serializers import InvoiceSerializer, InvoiceStatusSerializer


class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Invoice.objects.select_related("appointment__doctor__user", "appointment__patient__user").all().order_by("-created_at")
        user = self.request.user
        if user.role == "ADMIN":
            return qs
        if user.role == "DOCTOR":
            return qs.filter(appointment__doctor__user=user)
        if user.role == "PATIENT":
            return qs.filter(appointment__patient__user=user)
        return qs.none()

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied("Only admin can create invoices")
        serializer.save()


class InvoiceStatusUpdateView(generics.UpdateAPIView):
    serializer_class = InvoiceStatusSerializer
    queryset = Invoice.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        user = self.request.user
        invoice = self.get_object()

        if user.role == "ADMIN":
            # Admin can change any status
            serializer.save()
            return

        if user.role == "PATIENT":
            # Patient can only pay their own PENDING invoices
            if invoice.appointment.patient.user_id != user.id:
                raise PermissionDenied("You can only pay your own invoices")
            if invoice.status != "PENDING":
                raise PermissionDenied("This invoice is already " + invoice.status.lower())
            serializer.save(status="PAID", paid_at=timezone.now())
            return

        raise PermissionDenied("Not authorized to update invoice status")
