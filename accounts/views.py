from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import send_email_verification_email
from .models import EmailVerification
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view




class RegistrationView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Перевірка активації електронної пошти для даного користувача
        email_verification = EmailVerification.objects.filter(user__email=serializer.validated_data['email'], is_verified=True).first()

        if email_verification:
            return Response({'detail': 'Email is already verified. Please log in.'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.perform_create(serializer)

        # Генерація та відправлення листа для підтвердження електронної пошти
        send_email_verification_email(user)
        
        return Response({'detail': 'Registration successful. Email verification sent.'}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save()
        password = serializer.validated_data.get('password')
        if password:
            user.set_password(password)
            user.save()

        return user



class LoginView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # Отримання інформації для аутентифікації
        username = request.data.get("username")
        password = request.data.get("password")

        # Аутентифікація користувача
        user = authenticate(request, username=username, password=password)

        if user:
            try:
                email_verification = EmailVerification.objects.get(user=user)
                if email_verification.is_verified:
                    # Генеруємо токени доступу та оновлення
                    refresh = RefreshToken.for_user(user)

                    return Response({
                        'detail': 'Login successful.',
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Email not verified. Please verify your email.'}, status=status.HTTP_401_UNAUTHORIZED)
            except EmailVerification.DoesNotExist:
                return Response({'detail': 'Email verification not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class EmailVerificationView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, user_id, token, *args, **kwargs):
        email_verification = get_object_or_404(EmailVerification, user_id=user_id, verification_token=token)

        if email_verification.is_verified:
            return JsonResponse({'detail': 'Email already verified.'}, status=400)
        else:
            email_verification.is_verified = True
            email_verification.save()

            # Генеруємо токени
            user = email_verification.user
            refresh = RefreshToken.for_user(user)

            return JsonResponse({
                'detail': 'Email verified successfully.',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            })



class RefreshTokenView(APIView):

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access': access_token})
        except Exception as e:
            return Response({'error': 'Invalid token or token expired.'})



@api_view(['POST'])
def user_logout(request):
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response({'message': 'Refresh token not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)



def is_access_token_valid(access_token_str):
    try:
        access_token = AccessToken(access_token_str)
        # Якщо токен валідний, повернути True
        return True
    except Exception as e:
        # Якщо виникла помилка при перевірці токена, повернути False
        return False
