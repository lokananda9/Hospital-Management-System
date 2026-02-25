from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentStatusSerializer


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Appointment.objects.select_related("doctor__user", "patient__user").all().order_by("-start_time")
        user = self.request.user
        if user.role == "ADMIN":
            return qs
        if user.role == "DOCTOR":
            return qs.filter(doctor__user=user)
        if user.role == "PATIENT":
            return qs.filter(patient__user=user)
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "ADMIN":
            serializer.save()
            return
        if user.role == "PATIENT":
            patient = getattr(user, "patient_profile", None)
            if not patient:
                raise PermissionDenied("Patient profile is required")
            serializer.save(patient=patient)
            return
        raise PermissionDenied("Only admin or patient can create appointments")


class AppointmentStatusUpdateView(generics.UpdateAPIView):
    serializer_class = AppointmentStatusSerializer
    queryset = Appointment.objects.select_related("doctor__user").all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        user = self.request.user
        appointment = serializer.instance
        if user.role == "ADMIN":
            serializer.save()
            return
        if user.role == "DOCTOR" and appointment.doctor.user_id == user.id:
            serializer.save()
            return
        raise PermissionDenied("Only assigned doctor or admin can update status")
