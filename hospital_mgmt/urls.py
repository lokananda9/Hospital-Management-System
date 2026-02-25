from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="frontend"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("accounts.urls")),
    path("api/v1/", include("doctors.urls")),
    path("api/v1/", include("patients.urls")),
    path("api/v1/", include("appointments.urls")),
    path("api/v1/", include("prescriptions.urls")),
    path("api/v1/", include("billing.urls")),
    path("api/v1/", include("medicines.urls")),
    path("api/v1/", include("analytics.urls")),
]
