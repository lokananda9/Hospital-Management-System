from django.db import models

from appointments.models import Appointment
from common.models import TimeStampedModel


class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        VOID = "VOID", "Void"

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="invoice")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Doctor's fee")
    medicine_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Sum of medicines")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Tax on medicines")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount % applied")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount in ₹")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(max_length=40, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def calculate_totals(self):
        """Recalculate all totals from the prescription items."""
        subtotal = self.consultation_fee + self.medicine_total
        self.discount_amount = subtotal * self.discount_percent / 100
        self.total_amount = subtotal + self.tax - self.discount_amount

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)


INVOICE_STATUS_CHOICES = Invoice.Status.choices
