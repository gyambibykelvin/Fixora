from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking
from provider.models import Provider, Service
from account.models import User

# Create your views here.

#----------
# ROUTE: booking/ - Browse and create bookings
#----------
@login_required
def booking_view(request):
    """Display available providers/services and handle booking creation"""
    
    if request.method == "POST":
        provider_id = request.POST.get('provider_id')
        service_id = request.POST.get('service_id')
        service_type = request.POST.get('service_type')
        delivery_type = request.POST.get('delivery_type')
        service_date = request.POST.get('service_date')
        
        # Validate required fields
        if not all([provider_id, service_type, delivery_type]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('booking')
        
        try:
            selected_provider = Provider.objects.get(id=provider_id)
            
            # Create booking
            booking = Booking.objects.create(
                customer=request.user,
                provider=selected_provider,
                service=service_id if service_id else service_type,
                duration="",  # Can be set from service duration if needed
                status='pending',
                delivery_type=delivery_type,
                service_type=service_type,
            )
            
            messages.success(request, "Booking created successfully! Check your bookings for updates.")
            return redirect('my_bookings')
            
        except Provider.DoesNotExist:
            messages.error(request, "Selected provider not found.")
            return redirect('booking')
        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")
            return redirect('booking')
    
    # GET request - display available providers and services
    service_type = request.GET.get('service_type', '')
    
    # Get all active providers, filter by service_type if selected
    if service_type:
        providers = Provider.objects.filter(
            service_type=service_type, 
            status='active'
        )
    else:
        providers = Provider.objects.filter(status='active')
    
    # Get all available services
    services = Service.objects.filter(is_active=True)
    
    context = {
        'providers': providers,
        'services': services,
        'service_types': [
            ('barbering', 'Barbering'),
            ('laundry', 'Laundry'),
            ('cleaning', 'Cleaning'),
        ],
        'delivery_types': [
            ('home_delivery', 'Home Delivery'),
            ('pickup', 'Pickup'),
        ],
        'selected_service_type': service_type,
    }
    
    return render(request, 'booking/booking.html', context)


#----------
# ROUTE: my-bookings/ - View user's bookings
#----------
@login_required
def my_bookings(request):
    """Display all bookings for the logged-in user"""
    
    # Get filter from query parameter
    status_filter = request.GET.get('status', '')
    
    bookings = Booking.objects.filter(customer=request.user).select_related('provider').order_by('-id')
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Separate bookings by status
    upcoming = bookings.filter(status__in=['pending', 'confirmed'])
    completed = bookings.filter(status='completed')
    cancelled = bookings.filter(status='cancelled')
    
    context = {
        'bookings': bookings,
        'upcoming_bookings': upcoming,
        'completed_bookings': completed,
        'cancelled_bookings': cancelled,
        'status_filter': status_filter,
        'status_choices': [
            ('', 'All Bookings'),
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
    }
    
    return render(request, 'booking/my_bookings.html', context)


#----------
# ROUTE: booking-detail/<id>/ - View booking details
#----------
@login_required
def booking_detail(request, booking_id):
    """Display details of a specific booking"""
    
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'booking/booking_detail.html', context)


#----------
# ROUTE: cancel-booking/<id>/ - Cancel a booking
#----------
@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    # Only allow cancellation if booking is not completed or already cancelled
    if booking.status in ['completed', 'cancelled']:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == "POST":
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my_bookings')
    
    return render(request, 'booking/cancel_booking.html', {'booking': booking})


#----------
# ROUTE: browse-providers/ - Browse all providers
#----------
@login_required
def browse_providers(request):
    """Browse and filter providers"""
    
    service_type = request.GET.get('service_type', '')
    delivery_type = request.GET.get('delivery_type', '')
    
    providers_list = Provider.objects.filter(status='active')
    
    if service_type:
        providers_list = providers_list.filter(service_type=service_type)
    
    if delivery_type:
        providers_list = providers_list.filter(delivery_type=delivery_type)
    
    # Sort by rating
    providers_list = providers_list.order_by('-rating')
    
    context = {
        'providers': providers_list,
        'service_types': [
            ('', 'All Services'),
            ('barbering', 'Barbering'),
            ('laundry', 'Laundry'),
            ('cleaning', 'Cleaning'),
        ],
        'delivery_types': [
            ('', 'All Delivery Types'),
            ('home_delivery', 'Home Delivery'),
            ('pickup', 'Pickup'),
        ],
        'selected_service_type': service_type,
        'selected_delivery_type': delivery_type,
    }
    
    return render(request, 'booking/browse_providers.html', context)


#----------
# ROUTE: provider-detail/<id>/ - View provider details and services
#----------
@login_required
def provider_detail(request, provider_id):
    """Display provider details and their services"""
    
    provider_obj = get_object_or_404(Provider, id=provider_id, status='active')
    services = Service.objects.filter(provider=provider_obj, is_active=True)
    
    context = {
        'provider': provider_obj,
        'services': services,
    }
    
    return render(request, 'booking/provider_detail.html', context)
    
