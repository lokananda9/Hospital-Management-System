from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserCreateSerializer, UserSerializer, UserStatusUpdateSerializer
from common.permissions import IsAdminRole

User = get_user_model()


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class PatientSignupView(generics.CreateAPIView):
    """Public endpoint for patient self-registration."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        serializer.save(role="PATIENT")


class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        return UserCreateSerializer if self.request.method == "POST" else UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role.upper())
        return qs


class UserStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = UserStatusUpdateSerializer
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(instance).data, status=status.HTTP_200_OK)
