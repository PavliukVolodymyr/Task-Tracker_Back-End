from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer, LoginSerializer, UserProfileSerializer
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import send_email_verification_email, is_access_token_valid
from .models import EmailVerification, UserProfile
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .utils import valid_user
from django.contrib.auth.models import User

 


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

            # Створення профілю якщо його немає
            profile, created = UserProfile.objects.get_or_create(user=user)

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




class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        # Перевірка валідності токену перед отриманням профілю
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]
        
        user = valid_user(access_token_str)

        # Отримання інформації зі стандартної моделі користувача
        user_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email' : user.email,
        }

        # Пошук профілю за ідентифікатором користувача
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=404)

        # Об'єднання даних профілю та дані зі стандартної моделі користувача
        combined_data = {'profile': UserProfileSerializer(profile).data, 'user': user_data}

        return Response(combined_data)



class EditUserView(APIView):

    def post(self, request, *args, **kwargs):
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Валідація та отримання користувача
        user = valid_user(access_token_str)

        if isinstance(user, Response):
            return user

        # Використання UserSerializer для оновлення користувача
        data = {'first_name': request.data.get('first_name', user.first_name),
                'last_name': request.data.get('last_name', user.last_name)}
        serializer = UserSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserProfilePhotoView(APIView):

    def get(self, request, *args, **kwargs):
        user = valid_user(request.headers.get('Authorization', '').split(' ')[1])
        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        photo_url = profile.photo.url if profile.photo else None

        absolute_photo_url = request.build_absolute_uri(photo_url) if photo_url else None

        return Response({'photo_url': absolute_photo_url}, status=status.HTTP_200_OK)



    def post(self, request, *args, **kwargs):
        user = valid_user(request.headers.get('Authorization', '').split(' ')[1])
        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)


        file_serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if file_serializer.is_valid():
            profile.photo = request.data.get('photo')
            profile.save()
            return Response({'detail': 'Photo uploaded successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
