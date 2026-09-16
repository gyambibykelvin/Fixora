from django.urls import path
from . import views

urlpatterns = [
    # Provider application
    path('apply/', views.provider_application, name='provider_application'),
    path('application/status/', views.provider_application_status,name='provider_application_status'),
    path('dashboard/', views.provider_dashboard, name='provider_dashboard'),
]
