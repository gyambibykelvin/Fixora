from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import(Provider, Service, ProviderApplication)
from booking.models import Booking
from django.contrib import messages
from django.utils.dateparse import parse_time


@login_required
def provider_application(request):

    # Already a provider?
    if Provider.objects.filter(user=request.user).exists():
        return redirect('provider_dashboard')

    # Check whether the user already has an application
    application = ProviderApplication.objects.filter(
        user=request.user
    ).first()

    # If application already exists
    if application:

        return render(
            request,
            'provider/provider_application_status.html',
            {
                'application': application
            }
        )

    # Submit application
    if request.method == 'POST':

        service_type = request.POST.get('service_type')
        service_mode = request.POST.get('service_mode')
        experience_years = request.POST.get('experience_years')
        bio = request.POST.get('bio')
        id_document = request.FILES.get('id_document')

        # Basic validation
        if not service_type:
            messages.error(
                request,
                'Please select a service category.'
            )

            return redirect('provider_application')

        if not service_mode:
            messages.error(
                request,
                'Please select a service mode.'
            )

            return redirect('provider_application')

        if not experience_years:
            messages.error(
                request,
                'Please enter your years of experience.'
            )

            return redirect('provider_application')

        if not bio:
            messages.error(
                request,
                'Please provide a short biography.'
            )

            return redirect('provider_application')

        if not id_document:
            messages.error(
                request,
                'Please upload your ID document.'
            )

            return redirect('provider_application')

        # Create application
        ProviderApplication.objects.create(
            user=request.user,
            service_type=service_type,
            service_mode=service_mode,
            experience_years=experience_years,
            bio=bio,
            id_document=id_document
        )

        messages.success(
            request,
            'Your provider application has been submitted successfully.'
        )

        return redirect('provider_application_status')

    return render(
        request,
        'provider/provider_application.html'
    )



# APPLICATION STATUS

@login_required
def provider_application_status(request):

    application = ProviderApplication.objects.filter(
        user=request.user
    ).first()

    # No application yet
    if not application:

        return redirect('provider_application')

    # If approved and provider exists
    if (
        application.status == ProviderApplication.Status.APPROVED
        and Provider.objects.filter(user=request.user).exists()
    ):
        return redirect('provider_dashboard')

    return render(
        request,
        'provider/provider_application_status.html',
        {
            'application': application
        }
    )


# PROVIDER DASHBOARD

@login_required
def provider_dashboard(request):
    provider = Provider.objects.filter(user=request.user).first()

    if provider is None:
        application = ProviderApplication.objects.filter(
            user=request.user
        ).first()

        if application and application.status == ProviderApplication.Status.APPROVED:
            provider = Provider.objects.create(
                user=request.user,
                full_name=request.user.full_name,
                email=request.user.email,
                phone_number=request.user.phone_number,
                service_type=application.service_type,
                service_mode=application.service_mode,
                delivery_type=(
                    'home_service'
                    if application.service_mode == 'home'
                    else 'walk-in'
                ),
                address=request.user.address,
                bio=application.bio,
                working_hours='Not specified',
            )
        elif application:
            return redirect('provider_application_status')
        else:
            return redirect('provider_application')

    if request.method == 'POST':
        start_time = parse_time(request.POST.get('availability_start', ''))
        end_time = parse_time(request.POST.get('availability_end', ''))

        if start_time is None or end_time is None or start_time >= end_time:
            messages.error(request, 'Choose a valid start time and a later end time.')
            return redirect('provider_dashboard')

        provider.working_hours = (
            f'{start_time.strftime("%H:%M")}-{end_time.strftime("%H:%M")}'
        )
        provider.save(update_fields=['working_hours'])
        messages.success(request, 'Your available hours have been saved.')
        return redirect('provider_dashboard')


    # All bookings belonging to this provider
    bookings = Booking.objects.filter(provider=provider).order_by("-booking_date", "-booking_time")

    # Booking status groups
    pending_bookings = bookings.filter(status="pending")
    confirmed_bookings = bookings.filter(status="confirmed")
    completed_bookings = bookings.filter(status="completed")
    cancelled_bookings = bookings.filter(status="cancelled")

    # Services offered by provider
    services = Service.objects.filter(provider=provider)

    # Statistics
    total_bookings = bookings.count()
    pending_count = pending_bookings.count()
    completed_count = completed_bookings.count()
    availability_start = '09:00'
    availability_end = '17:00'
    if '-' in provider.working_hours:
        saved_start, saved_end = provider.working_hours.split('-', 1)
        parsed_start = parse_time(saved_start)
        parsed_end = parse_time(saved_end)
        if parsed_start and parsed_end:
            availability_start = parsed_start.strftime('%H:%M')
            availability_end = parsed_end.strftime('%H:%M')
    elif ',' in provider.working_hours:
        saved_times = [
            parse_time(value.strip())
            for value in provider.working_hours.split(',')
        ]
        saved_times = [value for value in saved_times if value]
        if saved_times:
            availability_start = min(saved_times).strftime('%H:%M')
            availability_end = max(saved_times).strftime('%H:%M')

    context = {
        "provider": provider,
        "profile": provider,

        # Bookings
        "bookings": bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,

        # Services
        "services": services,

        # Statistics
        "total_bookings": total_bookings,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "availability_start": availability_start,
        "availability_end": availability_end,
    }

    return render(request, "provider/provider_dashboard.html", context)


@login_required
@require_POST
def update_booking_status(request, booking_id, status):
    provider = Provider.objects.filter(user=request.user).first()
    if provider is None:
        messages.error(request, 'You are not registered as a provider.')
        return redirect('dashboard')

    booking = Booking.objects.filter(
        id=booking_id,
        provider=provider,
    ).first()
    if booking is None:
        messages.error(request, 'Booking not found.')
        return redirect('provider_dashboard')

    allowed_transitions = {
        'confirmed': {'pending'},
        'cancelled': {'pending', 'confirmed'},
        'completed': {'confirmed'},
    }
    if booking.status not in allowed_transitions.get(status, set()):
        messages.error(request, 'This booking cannot be updated in its current state.')
        return redirect('provider_dashboard')

    booking.status = status
    booking.save(update_fields=['status'])
    messages.success(request, f'Booking {status} successfully.')
    return redirect('provider_dashboard')

@login_required
def provider_profile_view(request):
    user = request.user

    if request.method == "POST":
       full_name = request.get("full_name", "").strip(),
       phone_number = request.get("phone_number", "").strip(),
       email = request.get("email", "").strip, 
       address = request.get("address", "").strip(),
       service_mode = request.get("service_mode", "").strip(),
       working_hours = request.get("working_hours", "").strip

       if not full_name or not address or not email:
         messages.info(request, "Name, address or email are required")
         return render(request,"provider/provider_dashboard", {user:user})

       if Provider.objects.filter(email=email).exclude(pk=user.pk).exists():
           messages.info(request, "Email is already in use", {user:user})
           return render(request, "provider/provider_dashboard")
       
       if not phone_number.isdigit() or len(phone_number) != 10:
                   messages.error(request, "Phone number must contain exactly 10 digits.")
                   return render(request, "account/profile.html", {"user": user})

       user.full_name = full_name
       user.email = email
       user.phone_number = phone_number
       user.address = address
    # if profile_picture:
    #    user.profile_picture = profile_picture
       user.save()
       
       messages.success(request, "Your profile has been updated.")
       return redirect("profile")
       
    return render(request, "account/profile.html", {"user": user})
           

