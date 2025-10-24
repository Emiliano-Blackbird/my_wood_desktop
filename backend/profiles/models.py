from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class UserProfile(models.Model):
    """Perfil de usuario: relación 1:1, amigos y seguimiento."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('usuario'),
    )
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profile_pictures/',
        null=True,
        blank=True,
    )
    bio = models.TextField(
        _('bio'),
        max_length=500,
        blank=True,
        help_text=_('Breve descripción del usuario.'),
    )

    friends = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
        verbose_name=_('amigos'),
    )

    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        verbose_name=_('siguiendo'),
    )

    class Meta:
        verbose_name = _('perfil')
        verbose_name_plural = _('perfiles')

    def __str__(self):
        return f'{self.user.username}'

    def send_friend_request(self, to_profile):
        """
        Crear solicitud si no existe, no es a sí mismo y no sois ya amigos.
        Si existe una solicitud inversa pendiente, se acepta automáticamente.
        """
        from .models import FriendRequest  # evita import circular en algunos entornos

        if self == to_profile:
            return None
        if self.is_friend(to_profile):
            return None

        # Si la otra persona ya envió una solicitud pendiente, aceptarla
        inverse = FriendRequest.objects.filter(
            from_user=to_profile,
            to_user=self,
            status=FriendRequest.STATUS_PENDING,
        ).first()
        if inverse:
            with transaction.atomic():
                inverse.accept()
            return inverse

        fr, created = FriendRequest.objects.get_or_create(
            from_user=self,
            to_user=to_profile,
            defaults={'status': FriendRequest.STATUS_PENDING},
        )
        return fr if created else None

    def remove_friend(self, other_profile):
        """
        Quitar amistad; dado que friends es symmetrical=True,
        basta remover en un lado.
        """
        if other_profile in self.friends.all():
            self.friends.remove(other_profile)

    def is_friend(self, other_profile):
        return other_profile in self.friends.all()

    # Follow utilities
    def follow(self, profile):
        if self != profile:
            self.following.add(profile)

    def unfollow(self, profile):
        self.following.remove(profile)

    def is_following(self, profile):
        return profile in self.following.all()


class FriendRequest(models.Model):
    STATUS_PENDING = 'P'
    STATUS_ACCEPTED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_ACCEPTED, _('Accepted')),
        (STATUS_REJECTED, _('Rejected')),
    ]

    from_user = models.ForeignKey(
        UserProfile,
        related_name='sent_requests',
        on_delete=models.CASCADE,
        verbose_name=_('usuario que envía'),
    )
    to_user = models.ForeignKey(
        UserProfile,
        related_name='received_requests',
        on_delete=models.CASCADE,
        verbose_name=_('usuario receptor'),
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_('estado'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('creada'),
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('respondida'),
    )

    class Meta:
        unique_together = ('from_user', 'to_user')  # evitar duplicados
        verbose_name = _('solicitud de amistad')
        verbose_name_plural = _('solicitudes de amistad')

    def __str__(self):
        return (
            f"{self.from_user.user.username} -> "
            f"{self.to_user.user.username} ({self.get_status_display()})"
        )

    @transaction.atomic
    def accept(self):
        """
        Aceptar solicitud de forma atómica. Añadir la relación de amistad
        en un solo lado es suficiente porque la relación es simétrica.
        """
        if self.status != self.STATUS_PENDING:
            return False

        self.from_user.friends.add(self.to_user)
        self.status = self.STATUS_ACCEPTED
        self.responded_at = timezone.now()
        self.save()
        return True

    def reject(self):
        if self.status != self.STATUS_PENDING:
            return False
        self.status = self.STATUS_REJECTED
        self.responded_at = timezone.now()
        self.save()
        return True


# Señal para crear UserProfile automáticamente al crear un User
@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
