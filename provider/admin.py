from django.contrib import admin
from .models import ProviderApplication, Provider

# Register your models here.

#admin.site.register(ProviderApplication)
#admin.site.register(Provider)

from django.contrib import admin

from .models import (
    ProviderApplication,
    Provider,
    Service
)


@admin.register(ProviderApplication)
class ProviderApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'service_type',
        'service_mode',
        'experience_years',
        'status',
        'submitted_at',
    )

    list_filter = (
        'status',
        'service_type',
        'service_mode',
    )

    search_fields = (
        'user__email',
        'user__full_name',
    )


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'email',
        'service_type',
        'service_mode',
        'status',
        'rating',
    )

    list_filter = (
        'status',
        'service_type',
        'service_mode',
    )

    search_fields = (
        'full_name',
        'email',
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'provider',
        'price',
        'duration',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'provider__full_name',
    )
