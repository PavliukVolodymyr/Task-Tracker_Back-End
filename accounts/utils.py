import secrets

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from .models import EmailVerification
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from django.contrib.auth.models import User



current_domain = "vaabr5.pythonanywhere.com"


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




def get_user_id_from_token(token):
    try:
        # Використовуйте AccessToken для декодування токена
        decoded_token = AccessToken(token)

        # Отримайте user_id з декодованого токена
        user_id = decoded_token['user_id']

        return user_id
    except Exception as e:
        print(f"Помилка декодування токена: {e}")
        return None



def is_access_token_valid(access_token_str):
    try:
        access_token = AccessToken(access_token_str)
        # Якщо токен валідний, повернути True
        return True
    except Exception as e:
        # Якщо виникла помилка при перевірці токена, повернути False
        return False



def valid_user(access_token_str):
    if not is_access_token_valid(access_token_str):
        return Response({'detail': 'Invalid access token.'}, status=401)

    # Отримання ідентифікатора користувача з токену
    user_id = get_user_id_from_token(access_token_str)

    # Пошук користувача за ідентифікатором
    try:
        user = User.objects.get(pk=user_id)
        return user
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=404)

