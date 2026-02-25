from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Patient

User = get_user_model()


class PatientSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "date_of_birth",
            "gender",
            "blood_group",
            "address",
            "emergency_contact",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "user_email", "user_name")
        extra_kwargs = {"user": {"required": False}}

    def validate_user(self, value):
        if value.role != User.Role.PATIENT:
            raise serializers.ValidationError("User role must be PATIENT")
        return value
