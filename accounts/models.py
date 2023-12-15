from django.db import models
from django.contrib.auth.models import User



class EmailVerification(models.Model):
    '''Модель перевірки верефікації'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(default='')

    def __str__(self):
        return self.user.username



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username