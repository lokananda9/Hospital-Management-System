from decimal import Decimal

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from billing.models import Invoice
from medicines.models import SystemSettings

from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Prescription.objects.select_related(
            "appointment__doctor__user", "appointment__patient__user"
        ).prefetch_related("items__medicine").all().order_by("-created_at")
        user = self.request.user
        if user.role == "ADMIN":
            return qs
        if user.role == "DOCTOR":
            return qs.filter(appointment__doctor__user=user)
        if user.role == "PATIENT":
            return qs.filter(appointment__patient__user=user)
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "ADMIN":
            prescription = serializer.save(created_by=user)
            self._generate_invoice(prescription)
            return
        if user.role == "DOCTOR":
            appointment = serializer.validated_data["appointment"]
            if appointment.doctor.user_id != user.id:
                raise PermissionDenied("Doctors can prescribe only for their appointments")
            prescription = serializer.save(created_by=user)
            self._generate_invoice(prescription)
            return
        raise PermissionDenied("Only doctor or admin can create prescriptions")

    def _generate_invoice(self, prescription):
        """Auto-generate an invoice from the prescription."""
        appointment = prescription.appointment

        # Skip if invoice already exists for this appointment
        if hasattr(appointment, "invoice"):
            return

        # Doctor consultation fee
        consultation_fee = appointment.doctor.consultation_fee or Decimal("0")

        # Sum up medicine costs and taxes
        medicine_total = Decimal("0")
        tax_total = Decimal("0")
        for item in prescription.items.select_related("medicine").all():
            item_cost = item.unit_price * item.quantity
            item_tax = item_cost * item.tax_percent / 100
            medicine_total += item_cost
            tax_total += item_tax

        # Get admin-configured discount
        settings = SystemSettings.get_settings()
        discount_percent = settings.discount_percent

        Invoice.objects.create(
            appointment=appointment,
            consultation_fee=consultation_fee,
            medicine_total=medicine_total,
            tax=tax_total,
            discount_percent=discount_percent,
        )


class PrescriptionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PrescriptionSerializer
    queryset = Prescription.objects.select_related(
        "appointment__doctor__user", "appointment__patient__user", "created_by"
    ).prefetch_related("items__medicine")
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == "ADMIN":
            return obj
        if user.role == "DOCTOR" and obj.appointment.doctor.user_id == user.id:
            return obj
        if user.role == "PATIENT" and obj.appointment.patient.user_id == user.id:
            return obj
        raise PermissionDenied("Not allowed to access this prescription")

    def perform_update(self, serializer):
        user = self.request.user
        prescription = serializer.instance
        if user.role == "ADMIN" or prescription.created_by_id == user.id:
            serializer.save()
            return
        raise PermissionDenied("Only author doctor or admin can update prescription")
