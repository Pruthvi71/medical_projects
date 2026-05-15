from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from django.urls import reverse
import re


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise OSError('SMTP unavailable')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(TestCase):
    def test_password_reset_sends_email_to_registered_user(self):
        User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='StrongPass123'
        )

        response = self.client.post(reverse('password_reset'), {
            'email': 'patient@example.com'
        })

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your VRAJ Care password', mail.outbox[0].subject)
        self.assertIn('reset/', mail.outbox[0].body)

    @override_settings(PUBLIC_SITE_URL='https://medical-projects.onrender.com')
    def test_password_reset_uses_public_site_url_when_configured(self):
        User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='StrongPass123'
        )

        self.client.post(reverse('password_reset'), {
            'email': 'patient@example.com'
        })

        self.assertIn('https://medical-projects.onrender.com/accounts/reset/', mail.outbox[0].body)

    def test_password_reset_confirm_changes_password(self):
        user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='OldStrongPass123'
        )

        self.client.post(reverse('password_reset'), {
            'email': 'patient@example.com'
        })

        reset_path = re.search(
            r'https?://[^/]+(?P<path>/accounts/reset/[^\s]+)',
            mail.outbox[0].body
        ).group('path')
        response = self.client.post(reset_path, {
            'new_password1': 'NewStrongPass123',
            'new_password2': 'NewStrongPass123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password changed successfully')
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPass123'))

    def test_password_reset_confirm_shows_error_for_mismatched_passwords(self):
        user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='OldStrongPass123'
        )

        self.client.post(reverse('password_reset'), {
            'email': 'patient@example.com'
        })

        reset_path = re.search(
            r'https?://[^/]+(?P<path>/accounts/reset/[^\s]+)',
            mail.outbox[0].body
        ).group('path')
        response = self.client.post(reset_path, {
            'new_password1': 'NewStrongPass123',
            'new_password2': 'DifferentPass123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Both passwords must match')
        self.assertContains(response, 'Password was not changed')
        user.refresh_from_db()
        self.assertFalse(user.check_password('NewStrongPass123'))

    def test_password_reset_does_not_send_email_for_unknown_address(self):
        response = self.client.post(reverse('password_reset'), {
            'email': 'missing@example.com'
        })

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_password_reset_warns_when_email_uses_console_backend(self):
        User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='StrongPass123'
        )

        response = self.client.post(reverse('password_reset'), {
            'email': 'patient@example.com'
        }, follow=True)

        message_text = ' '.join(str(message) for message in get_messages(response.wsgi_request))
        self.assertIn('server terminal', message_text)

    @override_settings(EMAIL_BACKEND='accounts.tests.FailingEmailBackend')
    def test_password_reset_shows_error_when_email_backend_fails(self):
        User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='StrongPass123'
        )

        response = self.client.post(reverse('password_reset'), {
            'email': 'patient@example.com'
        })

        self.assertEqual(response.status_code, 200)
        message_text = ' '.join(str(message) for message in get_messages(response.wsgi_request))
        self.assertIn('could not be sent', message_text)
