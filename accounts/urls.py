from django.urls import path

from .views import LoginView, MeView, PatientSignupView, RefreshView, UserListCreateView, UserStatusUpdateView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/signup/", PatientSignupView.as_view(), name="patient-signup"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/status/", UserStatusUpdateView.as_view(), name="user-status-update"),
]
