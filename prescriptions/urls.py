from django.urls import path

from .views import PrescriptionListCreateView, PrescriptionDetailView

urlpatterns = [
    path("prescriptions/", PrescriptionListCreateView.as_view(), name="prescription-list-create"),
    path("prescriptions/<int:pk>/", PrescriptionDetailView.as_view(), name="prescription-detail"),
]
