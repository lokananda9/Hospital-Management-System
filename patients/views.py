from django.conf import settings
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdminRole

from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Patient.objects.select_related("user").all()
        user = self.request.user
        if user.role == "ADMIN":
            return qs
        if user.role == "PATIENT":
            return qs.filter(user=user)
        if user.role == "DOCTOR":
            return qs
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "ADMIN":
            if not serializer.validated_data.get("user"):
                raise ValidationError({"user": "This field is required for admin-created patient profiles."})
            serializer.save()
            return
        if settings.PATIENT_SELF_SIGNUP_ENABLED and user.role == "PATIENT":
            serializer.save(user=user)
            return
        raise PermissionDenied("Not allowed to create patient profile")


class PatientDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    queryset = Patient.objects.select_related("user").all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user.role == "ADMIN" or obj.user_id == self.request.user.id:
            return obj
        raise PermissionDenied("Not allowed to access this patient profile")

    def perform_update(self, serializer):
        if self.request.user.role == "ADMIN":
            serializer.save()
            return
        if serializer.instance.user_id == self.request.user.id:
            serializer.save(user=self.request.user)
            return
        raise PermissionDenied("Not allowed to update this patient profile")
