from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdminRole

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.select_related("user").all().order_by("-created_at")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role in ["ADMIN", "PATIENT"]:
            return qs
        if user.role == "DOCTOR":
            return qs.filter(user=user)
        return qs.none()


class DoctorDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.select_related("user").all()

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAdminRole()]
        return [IsAuthenticated()]
