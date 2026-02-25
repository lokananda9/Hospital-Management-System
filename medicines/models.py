from django.db import models

from common.models import TimeStampedModel


class Medicine(TimeStampedModel):
    """Catalog of medicines with price and tax info."""

    class Category(models.TextChoices):
        TABLET = "TABLET", "Tablet"
        CAPSULE = "CAPSULE", "Capsule"
        SYRUP = "SYRUP", "Syrup"
        INJECTION = "INJECTION", "Injection"
        OINTMENT = "OINTMENT", "Ointment"
        DROPS = "DROPS", "Drops"
        INHALER = "INHALER", "Inhaler"
        SURGICAL = "SURGICAL", "Surgical Item"
        LAB_TEST = "LAB_TEST", "Lab Test"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.TABLET)
    manufacturer = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit price in ₹")
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=12.00, help_text="GST/tax percentage")
    requires_prescription = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category}) - ₹{self.price}"


class SystemSettings(models.Model):
    """Singleton settings - only one row should exist."""
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Global discount percentage applied to all invoices"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"Discount: {self.discount_percent}%"

    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
