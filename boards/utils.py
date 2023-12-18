from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from django.contrib.auth.models import User
from accounts.models import EmailVerification




def check_valid_user_email(user):
    if user:
        try:
            email_verification = EmailVerification.objects.get(user=user)
            if email_verification.is_verified:
                return True
            else:
                return Response({'detail': 'User email is not verified.'}, status=status.HTTP_403_FORBIDDEN)
        except EmailVerification.DoesNotExist:
            return Response({'detail': 'Email verification record not found for the user.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'detail': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)



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

