from django.contrib import admin

from .models import Medicine, SystemSettings

admin.site.register(Medicine)
admin.site.register(SystemSettings)
