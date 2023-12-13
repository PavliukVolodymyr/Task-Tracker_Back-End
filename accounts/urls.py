from django.urls import path
from .views import RegistrationView, LoginView
from .views import EmailVerificationView, RefreshTokenView
from .views import user_logout


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-verification/<int:user_id>/<str:token>/', EmailVerificationView.as_view(), name='email-verification-confirm'),
    path('email-verification/', EmailVerificationView.as_view(), name='email-verification'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('logout/', user_logout, name='user-logout'),

]
