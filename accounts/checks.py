from django.conf import settings
from django.core.checks import Warning, register


@register()
def password_reset_email_settings_check(app_configs, **kwargs):
    warnings = []

    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        warnings.append(
            Warning(
                'Password reset emails are configured for console output only.',
                hint='Create a .env file with EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to send reset emails to inboxes.',
                id='accounts.W001',
            )
        )

    if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
        missing = [
            name for name in ('EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD')
            if not getattr(settings, name, '')
        ]
        if missing:
            warnings.append(
                Warning(
                    'SMTP email backend is enabled but required credentials are missing.',
                    hint=f'Set {", ".join(missing)} in your .env file or deployment environment.',
                    id='accounts.W002',
                )
            )

    return warnings
