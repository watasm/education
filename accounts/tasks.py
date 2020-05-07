import logging
from django.urls import reverse
from django.core.mail import send_mail
from education.celery import app
from accounts.models import Profile
from django.contrib.auth.models import User
from education.settings.local import EMAIL_HOST_USER

@app.task
def send_verification_email(profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
        send_mail(
            'Verify your E-learning account',
            'Follow this link to verify your account: '
            'http://127.0.0.1:8000%s' % reverse('verify', kwargs={'uuid': str(profile.verification_uuid)}),
            EMAIL_HOST_USER,
            [profile.user.email],
            fail_silently=False,
        )
    except Profile.DoesNotExist:
        logging.warning("Tried to send verification email to non-existing user '%s'" % user_id)
