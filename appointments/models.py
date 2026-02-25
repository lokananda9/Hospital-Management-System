from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F

from common.models import TimeStampedModel
from doctors.models import Doctor
from patients.models import Patient


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(end_time__gt=F("start_time")), name="appointment_end_after_start"),
        ]
        indexes = [
            models.Index(fields=["doctor", "start_time"]),
            models.Index(fields=["patient", "start_time"]),
            models.Index(fields=["status"]),
        ]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("end_time must be greater than start_time")
        overlap_qs = Appointment.objects.filter(
            doctor=self.doctor,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if self.pk:
            overlap_qs = overlap_qs.exclude(pk=self.pk)
        if overlap_qs.exists():
            raise ValidationError("Doctor has overlapping appointment")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


APPOINTMENT_STATUS_CHOICES = Appointment.Status.choices
