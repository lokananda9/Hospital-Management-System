from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)
    patient_name = serializers.CharField(source="patient.user.full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "doctor",
            "doctor_name",
            "patient",
            "patient_name",
            "start_time",
            "end_time",
            "reason",
            "notes",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {"patient": {"required": False}}

    def validate(self, attrs):
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({"end_time": "end_time must be greater than start_time"})
        if doctor and start_time and end_time:
            qs = Appointment.objects.filter(doctor=doctor, start_time__lt=end_time, end_time__gt=start_time)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Doctor has overlapping appointment")
        return attrs


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ("status",)
