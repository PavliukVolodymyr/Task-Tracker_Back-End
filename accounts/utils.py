import secrets

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from .models import EmailVerification
from django.conf import settings



def generate_token():
    # Генеруємо токен з 20-значною довжиною
    return secrets.token_urlsafe(20)



def send_email_verification_email(user):
    subject = 'Email Verification'
    
    # Створюємо URL для підтвердження електронної пошти
    email_verification = EmailVerification.objects.create(user=user, email=user.email)
    email_verification.verification_token = generate_token()
    email_verification.save()


    verification_link = reverse('email-verification-confirm', kwargs={'user_id': user.id, 'token': email_verification.verification_token})
    full_verification_link = f'http://{current_domain}{verification_link}'

    # Створюємо текстовий лист
    message = f'Please click the link below to verify your email:\n\n{full_verification_link}'
    
    from_email = settings.EMAIL_HOST_USER
    to_email = user.email

    send_mail(
        subject,
        message,
        from_email,
        [to_email],
        fail_silently=False,
    )