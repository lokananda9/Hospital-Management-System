from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Doctor

User = get_user_model()


class DoctorSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "specialization",
            "license_number",
            "years_experience",
            "consultation_fee",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "user_email", "user_name")

    def validate_user(self, value):
        if value.role != User.Role.DOCTOR:
            raise serializers.ValidationError("User role must be DOCTOR")
        return value
