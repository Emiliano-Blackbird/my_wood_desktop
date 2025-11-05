from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PomodoroSettings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_pomodoro_settings(sender, instance, created, **kwargs):
    if created:
        PomodoroSettings.objects.create(user=instance)
