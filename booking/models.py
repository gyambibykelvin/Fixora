from django.db import models
from account.models import User
from provider.models import provider
# Create your models here.

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking')
    provider = models.ForeignKey(provider, on_delete=models.CASCADE)
    service = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    delivery_type =models.CharField(max_length=100)
    service_type = models.CharField(max_length=100)