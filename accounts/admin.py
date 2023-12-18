from django.contrib import admin
from .models import EmailVerification, UserProfile



@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'verification_token', 'email']
    search_fields = ['user__username', 'email']



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo']
    search_fields = ['user__username']
