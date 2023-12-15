from django.urls import path
from .views import RegistrationView, LoginView
from .views import EmailVerificationView, RefreshTokenView
from .views import user_logout, UserProfileView, EditUserView
from .views import UserProfilePhotoView



urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-verification/<int:user_id>/<str:token>/', EmailVerificationView.as_view(), name='email-verification-confirm'),
    path('email-verification/', EmailVerificationView.as_view(), name='email-verification'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('logout/', user_logout, name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', EditUserView.as_view(), name='edit-user'),
    path('profile/photo/', UserProfilePhotoView.as_view(), name='user-profile-photo'),
    path('profile/photo/edit/', UserProfilePhotoView.as_view(), name='user-profile-photo'),

] 

