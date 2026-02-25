from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Sum
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment
from billing.models import Invoice
from common.permissions import IsAdminRole

from .serializers import DashboardOverviewSerializer

User = get_user_model()


class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    @extend_schema(responses=DashboardOverviewSerializer)
    def get(self, request):
        # Skip cache so payments reflect immediately
        users_by_role = {row["role"]: row["total"] for row in User.objects.values("role").annotate(total=Count("id"))}
        appointments_by_status = {
            row["status"]: row["total"] for row in Appointment.objects.values("status").annotate(total=Count("id"))
        }

        paid_agg = Invoice.objects.filter(status="PAID").aggregate(total=Sum("total_amount"), count=Count("id"))
        pending_agg = Invoice.objects.filter(status="PENDING").aggregate(total=Sum("total_amount"), count=Count("id"))

        payload = {
            "users_by_role": users_by_role,
            "appointments_by_status": appointments_by_status,
            "revenue_paid_total": str(Decimal(paid_agg["total"] or 0)),
            "total_invoices": Invoice.objects.count(),
            "paid_count": paid_agg["count"] or 0,
            "pending_count": pending_agg["count"] or 0,
            "pending_amount": str(Decimal(pending_agg["total"] or 0)),
        }
        return Response(payload)
