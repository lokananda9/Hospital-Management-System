from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole

from .models import Medicine, SystemSettings
from .serializers import MedicineSerializer, SystemSettingsSerializer


class MedicineListCreateView(generics.ListCreateAPIView):
    """GET: all authenticated users can list active medicines. POST: admin only."""
    serializer_class = MedicineSerializer

    def get_queryset(self):
        qs = Medicine.objects.all()
        if self.request.user.role != "ADMIN":
            qs = qs.filter(is_active=True)
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [IsAuthenticated()]


class MedicineDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: authenticated, PUT/PATCH/DELETE: admin only."""
    serializer_class = MedicineSerializer
    queryset = Medicine.objects.all()

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdminRole()]
        return [IsAuthenticated()]


class SystemSettingsView(APIView):
    """GET: any authenticated user. PUT/PATCH: admin only."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings = SystemSettings.get_settings()
        return Response(SystemSettingsSerializer(settings).data)

    def put(self, request):
        if request.user.role != "ADMIN":
            return Response({"detail": "Only admin can update settings"}, status=status.HTTP_403_FORBIDDEN)
        settings = SystemSettings.get_settings()
        serializer = SystemSettingsSerializer(settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        return self.put(request)
