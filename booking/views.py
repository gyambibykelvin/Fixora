from datetime import time as datetime_time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from .models import Booking
from provider.models import Provider, Service
from account.models import User

# Create your views here.

# ROUTE: booking/ - Browse and create bookings
@login_required
def booking_view(request):
    """Display available providers/services and handle booking creation"""
    
    if request.method == "POST":
        provider_id = request.POST.get('provider_id')
        service_id = request.POST.get('service_id')
        service_type = request.POST.get('service_type')
        delivery_type = request.POST.get('delivery_type')
        service_date = request.POST.get('service_date')
        service_time = request.POST.get('service_time')
        
        # Validate required fields
        if not all([provider_id, service_type, delivery_type, service_date, service_time]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('dashboard')

        booking_date = parse_date(service_date)
        booking_time = parse_time(service_time)
        if booking_date is None or booking_time is None or booking_date < timezone.localdate():
            messages.error(request, "Please select a valid future date and time.")
            return redirect('dashboard')

        service_mode_by_delivery = {
            'home_delivery': Provider.ServiceMode.HOME,
            'pickup': Provider.ServiceMode.WALK_IN,
        }
        if delivery_type not in service_mode_by_delivery:
            messages.error(request, "Please select a valid service mode.")
            return redirect('dashboard')
        
        try:
            selected_provider = Provider.objects.get(
                id=provider_id,
                service_type=service_type,
                status='active',
            )

            if selected_provider.service_mode not in {
                service_mode_by_delivery[delivery_type],
                Provider.ServiceMode.BOTH,
            }:
                messages.error(request, "Selected provider does not offer that service mode.")
                return redirect('dashboard')

            working_hours = selected_provider.working_hours
            if '-' in working_hours:
                start_value, end_value = working_hours.split('-', 1)
                start_time = parse_time(start_value.strip())
                end_time = parse_time(end_value.strip())
                if start_time is None or end_time is None or start_time >= end_time:
                    messages.error(request, "This provider has invalid available hours.")
                    return redirect('dashboard')

                start_minutes = start_time.hour * 60 + start_time.minute
                booking_minutes = booking_time.hour * 60 + booking_time.minute
                if (
                    booking_time < start_time
                    or booking_time >= end_time
                    or (booking_minutes - start_minutes) % 30 != 0
                ):
                    messages.error(request, "Please select a time within the provider's available hours.")
                    return redirect('dashboard')
            else:
                available_times = {
                    parse_time(value.strip())
                    for value in working_hours.split(',')
                    if parse_time(value.strip()) is not None
                }
                if booking_time not in available_times:
                    messages.error(request, "Please select one of the provider's available times.")
                    return redirect('dashboard')

            if not working_hours or working_hours == 'Not specified':
                messages.error(request, "Please select one of the provider's available times.")
                return redirect('dashboard')

            if (
                booking_date == timezone.localdate()
                and booking_time <= timezone.localtime().time().replace(
                    tzinfo=None,
                    second=0,
                    microsecond=0,
                )
            ):
                messages.error(request, "Please select a time that has not passed.")
                return redirect('dashboard')

            # Create booking
            booking = Booking.objects.create(
                customer=request.user,
                provider=selected_provider,
                service=service_id if service_id else service_type,
                duration="",  # Can be set from service duration if needed
                status='pending',
                delivery_type=delivery_type,
                service_type=service_type,
                booking_date=booking_date,
                booking_time=booking_time,
            )
            
            messages.success(request, "Booking created successfully! Check your bookings for updates.")
            return redirect('my_bookings')
            
        except Provider.DoesNotExist:
            messages.error(request, "Selected provider not found.")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")
            return redirect('dashboard')
    
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


@login_required
def provider_available_slots(request):
    provider_id = request.GET.get('provider_id')
    booking_date = parse_date(request.GET.get('date', ''))

    if not provider_id or booking_date is None or booking_date < timezone.localdate():
        return JsonResponse({'times': []})

    provider = Provider.objects.filter(id=provider_id, status='active').first()
    if provider is None:
        return JsonResponse({'times': []})

    now = timezone.localtime()
    current_time = now.time().replace(tzinfo=None, second=0, microsecond=0)
    times = []

    if '-' in provider.working_hours:
        start_value, end_value = provider.working_hours.split('-', 1)
        start_time = parse_time(start_value.strip())
        end_time = parse_time(end_value.strip())
        if start_time and end_time and start_time < end_time:
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            for minutes in range(start_minutes, end_minutes, 30):
                hour, minute = divmod(minutes, 60)
                slot_time = datetime_time(hour, minute)
                if (
                    booking_date != timezone.localdate()
                    or slot_time > current_time
                ):
                    times.append(slot_time.strftime('%H:%M'))

    return JsonResponse({'times': times})



# ROUTE: my-bookings/ - View user's bookings
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



# ROUTE: booking-detail/<id>/ - View booking details

@login_required
def booking_detail(request, booking_id):
    """Display details of a specific booking"""
    
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'booking/booking_detail.html', context)


# ROUTE: cancel-booking/<id>/ - Cancel a booking

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


# ROUTE: provider-detail/<id>/ - View provider details and services

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
    
