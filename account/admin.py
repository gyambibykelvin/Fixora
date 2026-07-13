from django.contrib import admin
from .models import User

# Register your models here.
class user(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number','password', 'address', 'profile_picture', 'status', 'created_at')

admin.site.register(User, user)