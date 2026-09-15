from django.db import models
from account.models import User

# Create your models here.

#-----------
#Provider Application if a user or business want to register or render service on the platform
#They ought to submit an application and they will get a provider's dashboard
#-----------

class ProviderApplication(models.Model):
    class Status(models.TextChoices):
        PENDING=  'pending', 'Pending'
        APPROVED= 'approved', 'Approved'
        REJECTED= 'rejected', 'Rejected'
    class ServiceType(models.TextChoices):
        BARBERING= 'barbering', 'Barbering'
        LAUNDRY= 'laundry', 'Laundry'
        CLEANING= 'cleaning', 'Cleaning'

    class ServiceMode(models.TextChoices):
        HOME = 'home', 'Home Service'
        WALK_IN = 'walk_in', 'Walk-in'


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='application')
    service_type = models.CharField(max_length=20, choices=[('barbering', 'Barbering'), ('laundry', 'Laundry'), ('cleaning', 'Cleaning')])
    service_mode = models.CharField(max_length=20, choices=ServiceMode.choices)
    experience_years = models.PositiveIntegerField()
    bio = models.TextField()
    id_document = models.ImageField(upload_to='applications/ids/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason=models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'provider_applications'

    def __str__(self):
        return f"{self.user.full_name} - {self.service_type} - ({self.status})"

class Provider(models.Model):
    class ServiceType(models.TextChoices):
        BARBERING= 'barbering', 'Barbering'
        LAUNDRY= 'laundry', 'Laundry'
        CLEANING= 'cleaning', 'Cleaning'

    class ServiceMode(models.TextChoices):
        HOME = 'home', 'Home Service'
        WALK_IN = 'walk_in', 'Walk-in'


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    full_name =models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=10)
    service_type=models.CharField(max_length=100, choices=[('barbering', 'Barbering'), ('laundry', 'Laundry'), ('cleaning', 'Cleaning')])
    service_mode=models.CharField(max_length=20, choices=[('home', 'Home Service'), ('walk_in', 'Walk-in')])
    delivery_type=models.CharField(max_length=20, choices=[('home_service', 'Home Service'), ('pickup', 'Pickup')])
    address=models.CharField(max_length=100)
    bio=models.TextField()
    profile_picture=models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    status=models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    rating=models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    availability=models.BooleanField(default=True)
    working_hours=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'providers'

    def __str__(self):
        return self.full_name
    
class Service(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    address = models.TextField(max_length=50)
    description = models.TextField(max_length=100)
    is_active= models.BooleanField(default=True)

    class Meta:
        db_table= 'services'
    
    def __str__(self):
        return self.name
     