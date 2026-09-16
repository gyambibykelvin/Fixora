from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import(Provider, Service, ProviderApplication)
from booking.models import Booking
from django.contrib import messages


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
                    else 'pickup'
                ),
                address=request.user.address,
                bio=application.bio,
                working_hours='Not specified',
            )
        elif application:
            return redirect('provider_application_status')
        else:
            return redirect('provider_application')


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
    }

    return render(request, "provider/provider_dashboard.html", context)
