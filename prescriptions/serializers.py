from rest_framework import serializers

from medicines.models import Medicine

from .models import Prescription, PrescriptionItem


class PrescriptionItemWriteSerializer(serializers.Serializer):
    """For creating prescription items — doctor sends medicine ID, qty, dosage, frequency."""
    medicine = serializers.PrimaryKeyRelatedField(queryset=Medicine.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1, default=1)
    dosage = serializers.CharField(max_length=100)
    frequency = serializers.CharField(max_length=100)
    duration_days = serializers.IntegerField(min_value=1, default=7)


class PrescriptionItemReadSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_category = serializers.CharField(source="medicine.category", read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_tax = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = (
            "id", "medicine", "medicine_name", "medicine_category",
            "quantity", "dosage", "frequency", "duration_days",
            "unit_price", "tax_percent", "line_total", "line_tax",
        )


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemReadSerializer(many=True, read_only=True)
    medicines = PrescriptionItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Prescription
        fields = (
            "id", "appointment", "diagnosis", "instructions",
            "items", "medicines",
            "created_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def create(self, validated_data):
        medicines_data = validated_data.pop("medicines", [])
        prescription = Prescription.objects.create(**validated_data)

        for med_data in medicines_data:
            medicine = med_data["medicine"]
            PrescriptionItem.objects.create(
                prescription=prescription,
                medicine=medicine,
                quantity=med_data.get("quantity", 1),
                dosage=med_data["dosage"],
                frequency=med_data["frequency"],
                duration_days=med_data.get("duration_days", 7),
                unit_price=medicine.price,       # Snapshot current price
                tax_percent=medicine.tax_percent, # Snapshot current tax
            )

        return prescription
