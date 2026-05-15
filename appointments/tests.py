from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from doctors.models import Doctor
from .models import Appointment


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AppointmentTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='StrongPass123'
        )
        doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='StrongPass123'
        )
        self.doctor = Doctor.objects.create(
            user=doctor_user,
            specialization='Cardiology',
            available=True
        )

    def test_booking_requires_login(self):
        response = self.client.get(reverse('book_appointment'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_patient_can_book_future_appointment(self):
        self.client.login(username='patient', password='StrongPass123')
        appointment_date = timezone.localdate() + timedelta(days=1)

        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.id,
            'date': appointment_date.isoformat(),
        })

        self.assertRedirects(response, reverse('my_appointments'))
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(Appointment.objects.first().status, 'Pending')

    def test_patient_cannot_book_past_appointment(self):
        self.client.login(username='patient', password='StrongPass123')
        appointment_date = timezone.localdate() - timedelta(days=1)

        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.id,
            'date': appointment_date.isoformat(),
        })

        self.assertRedirects(response, reverse('book_appointment'))
        self.assertEqual(Appointment.objects.count(), 0)

    def test_patient_can_cancel_only_pending_appointment(self):
        self.client.login(username='patient', password='StrongPass123')
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.localdate(),
            status='Pending'
        )

        response = self.client.post(reverse('cancel_appointment', args=[appointment.id]))

        self.assertRedirects(response, reverse('my_appointments'))
        self.assertFalse(Appointment.objects.filter(id=appointment.id).exists())
