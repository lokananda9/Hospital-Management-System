from django.urls import path

from .views import MedicineDetailView, MedicineListCreateView, SystemSettingsView

urlpatterns = [
    path("medicines/", MedicineListCreateView.as_view(), name="medicine-list"),
    path("medicines/<int:pk>/", MedicineDetailView.as_view(), name="medicine-detail"),
    path("settings/", SystemSettingsView.as_view(), name="system-settings"),
]
