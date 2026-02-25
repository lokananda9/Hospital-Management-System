from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")


class IsDoctorRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "DOCTOR")


class IsPatientRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "PATIENT")


class IsOwnerOrAdmin(BasePermission):
    user_attr = "user"

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        owner = getattr(obj, self.user_attr, None)
        return owner == request.user
