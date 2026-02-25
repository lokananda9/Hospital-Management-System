from django.urls import path

from .views import AppointmentListCreateView, AppointmentStatusUpdateView

urlpatterns = [
    path("appointments/", AppointmentListCreateView.as_view(), name="appointment-list-create"),
    path("appointments/<int:pk>/status/", AppointmentStatusUpdateView.as_view(), name="appointment-status-update"),
]
