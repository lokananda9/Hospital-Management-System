from django.conf import settings
from django.db import models

from appointments.models import Appointment
from common.models import TimeStampedModel


class Prescription(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="prescription")
    diagnosis = models.TextField()
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prescriptions")

    def __str__(self):
        return f"Prescription #{self.pk}"


class PrescriptionItem(TimeStampedModel):
    """Each medicine prescribed, linked to the medicine catalog."""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey("medicines.Medicine", on_delete=models.PROTECT, related_name="prescription_items")
    quantity = models.PositiveIntegerField(default=1)
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg")
    frequency = models.CharField(max_length=100, help_text="e.g. Twice daily")
    duration_days = models.PositiveIntegerField(default=7, help_text="Number of days")

    # Snapshot the price at the time of prescription (price may change later)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit at time of prescription")
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tax % at time of prescription")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def line_tax(self):
        return self.line_total * self.tax_percent / 100
