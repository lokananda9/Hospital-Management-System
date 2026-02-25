from rest_framework import serializers

from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = (
            "id", "appointment",
            "consultation_fee", "medicine_total", "tax",
            "discount_percent", "discount_amount", "total_amount",
            "status", "payment_method", "paid_at",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "consultation_fee", "medicine_total", "tax",
            "discount_percent", "discount_amount", "total_amount",
            "created_at", "updated_at",
        )


class InvoiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ("status", "payment_method", "paid_at")
