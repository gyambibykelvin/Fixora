from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_view, name='booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('browse-providers/', views.browse_providers, name='browse_providers'),
    path('provider/<int:provider_id>/', views.provider_detail, name='provider_detail'),
]
