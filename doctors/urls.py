from django.urls import path

from .views import DoctorDetailView, DoctorListCreateView

urlpatterns = [
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list-create"),
    path("doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctor-detail"),
]
