from rest_framework import serializers

from .models import Medicine, SystemSettings


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = (
            "id", "name", "generic_name", "category", "manufacturer",
            "price", "tax_percent", "requires_prescription", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ("discount_percent", "updated_at")
        read_only_fields = ("updated_at",)
