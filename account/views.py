from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User
from booking.models import Booking
from provider.models import Provider, ProviderApplication
import datetime
# Create your views here.

#ROUTES: signup/

def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        address = request.POST.get("address")
       # profile_picture = request.FILES.get("profile_picture")


        # Check if the email or already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "account/signup.html")

       # Check if the passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "account/signup.html")
        
        # Create a new user
        user = User.objects.create_user(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password=password1,
            address=address,
           # profile_picture=profile_picture,
        )

        # Redirect to the login page after successful signup
        messages.success(request, "Account has been successfully created! Login to continue")
        return redirect('login')
        

    return render(request, "account/signup.html")



#ROUTES: login/

def login_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            if not remember_me:
                #session expires when browser closes
                request.session.set_expiry(0)
            
            else:
                #session lasts for 30 days
                request.session.set_expiry(60 * 60 *24 * 30)

            messages.success(request, "You have successfully logged in.")

            if Provider.objects.filter(user=user).exists():
                return redirect("provider_dashboard")

            application = ProviderApplication.objects.filter(user=user).first()
            if application and application.status in {
                ProviderApplication.Status.PENDING,
                ProviderApplication.Status.APPROVED,
                ProviderApplication.Status.REJECTED,
            }:
                return redirect("provider_application_status")

            return redirect("dashboard")

        
        messages.error(request, "Invalid email or password.")
        return render(request, "account/login.html")

    return render(request, "account/login.html")


#ROUTES: logout/
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("login")

#-----------
#ROUTE: settings/
#-----------
@login_required
def settings_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone')
        profile_picture = request.user.profile_picture

        # Update the fields directly on the logged-in user object
        request.user.full_name = full_name
        request.user.phone_number = phone_number
        request.user.profile_picture = profile_picture
        request.user.save()

        messages.success(request, 'Your profile has been updated.')
        return redirect('accounts:settings')

    return render(request, 'accounts/settings.html', {'user': request.user})


@login_required
def dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).select_related('provider').order_by('-id')

    upcoming_bookings = bookings.filter(status__in=['pending', 'confirmed']).order_by('-id')
    completed_count = bookings.filter(status='completed').count()
    providers_used = bookings.values('provider').distinct().count()

    service_cards = [
        {
            'name': 'Barbering',
            'slug': 'barbering',
            'count': Provider.objects.filter(service_type='barbering').count(),
        },
        {
            'name': 'Laundry',
            'slug': 'laundry',
            'count': Provider.objects.filter(service_type='laundry').count(),
        },
        {
            'name': 'Cleaning',
            'slug': 'cleaning',
            'count': Provider.objects.filter(service_type='cleaning').count(),
        },
    ]

    available_providers = list(
        Provider.objects.filter(status='active').values(
            'id', 'full_name', 'rating', 'service_type'
        )
    )

    now = datetime.datetime.now()
    if now.hour < 12:
            greeting = 'Good morning'
    elif 12 <= now.hour < 18:
            greeting= 'Good afternoon'
    else:
            greeting = 'Good evening'

    context = {
        'user': request.user,
        'total_bookings': bookings.count(),
        'upcoming_count': upcoming_bookings.count(),
        'completed_count': completed_count,
        'providers_used': providers_used,
        'service_cards': service_cards,
        'available_providers': available_providers,
        'upcoming_bookings': upcoming_bookings[:5],
        'greeting': greeting,
    }

    return render(request, 'account/dashboard.html', context)


#profile
@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        profile_picture = request.FILES.get("profile_picture")
        full_name = request.POST.get("full_name", "").strip()
        address = request.POST.get("address", "").strip()

        if not full_name or not email or not address:
            messages.error(request, "Name, email, and address are required.")
            return render(request, "account/profile.html", {"user": user})

        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, "That email is already in use.")
            return render(request, "account/profile.html", {"user": user})

        if not phone_number.isdigit() or len(phone_number) != 10:
            messages.error(request, "Phone number must contain exactly 10 digits.")
            return render(request, "account/profile.html", {"user": user})

        if not address:
             messages.error(request, "Address is required")
             return render(request, "account/profile.html", {"user":user})
        user.full_name = full_name
        user.email = email
        user.phone_number = phone_number
        user.address = address
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()

        messages.success(request, "Your profile has been updated.")
        return redirect("profile")

    return render(request, "account/profile.html", {"user": user})