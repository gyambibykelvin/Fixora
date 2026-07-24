from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from booking.models import Booking
from provider.models import provider
# Create your views here.

#----------
#ROUTES: signup/
#----------
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



#----------
#ROUTES: login/
#----------

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
                request.session.set_expiry(o)
            
            else:
                #session lasts for 30 days
                request.session.set_expiry(60 * 60 *24 * 30)

            messages.success(request, "You have successfully logged in.")
            return redirect("dashboard")

        
        messages.error(request, "Invalid email or password.")
        return render(request, "account/login.html")

    return render(request, "account/login.html")

#----------
#ROUTES: logout/
#----------
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
            'count': provider.objects.filter(service_type='barbering').count(),
        },
        {
            'name': 'Laundry',
            'slug': 'laundry',
            'count': provider.objects.filter(service_type='laundry').count(),
        },
        {
            'name': 'Cleaning',
            'slug': 'cleaning',
            'count': provider.objects.filter(service_type='cleaning').count(),
        },
    ]

    context = {
        'user': request.user,
        'total_bookings': bookings.count(),
        'upcoming_count': upcoming_bookings.count(),
        'completed_count': completed_count,
        'providers_used': providers_used,
        'service_cards': service_cards,
        'upcoming_bookings': upcoming_bookings[:5],
    }

    return render(request, 'account/dashboard.html', context)