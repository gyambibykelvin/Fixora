from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from booking.models import Booking
from provider.models import provider


class BookingViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='customer@example.com',
            password='StrongPass123',
            full_name='Customer User',
            phone_number='0550000000',
            address='Accra'
        )
        self.provider = provider.objects.create(
            full_name='Jane Doe',
            email='provider@example.com',
            phone_number='0551111111',
            service_type='barbering',
            delivery_type='home_delivery',
            address='Kumasi',
            bio='Experienced barber',
            working_hours='9am-5pm'
        )

    def test_booking_page_requires_login(self):
        response = self.client.get(reverse('booking'))
        self.assertEqual(response.status_code, 302)

    def test_booking_page_lists_and_creates_bookings(self):
        self.client.login(email='customer@example.com', password='StrongPass123')

        response = self.client.get(reverse('booking'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book a Service')

        response = self.client.post(reverse('booking'), {
            'provider': self.provider.id,
            'service': 'Haircut',
            'duration': '30 mins',
            'status': 'pending',
            'delivery_type': 'home_delivery',
            'service_type': 'barbering',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.filter(customer=self.user, service='Haircut').exists())

    def test_my_bookings_page_shows_empty_state(self):
        self.client.login(email='customer@example.com', password='StrongPass123')

        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No bookings yet')
        self.assertContains(response, 'Explore services')
