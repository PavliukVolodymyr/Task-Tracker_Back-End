from django.urls import path
from .views import RegistrationView, LoginView, EmailVerificationView



urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-verification/<int:user_id>/<str:token>/', EmailVerificationView.as_view(), name='email-verification-confirm'),
    path('email-verification/', EmailVerificationView.as_view(), name='email-verification'),

]
