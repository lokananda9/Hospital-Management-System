from rest_framework import serializers


class DashboardOverviewSerializer(serializers.Serializer):
    users_by_role = serializers.DictField(child=serializers.IntegerField())
    appointments_by_status = serializers.DictField(child=serializers.IntegerField())
    revenue_paid_total = serializers.CharField()
    total_invoices = serializers.IntegerField()
