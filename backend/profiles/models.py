from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# Relación uno a uno con el modelo usuario
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField("Profile Picture", upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField("Bio", max_length=500, blank=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"
