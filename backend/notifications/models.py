from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """Notificaciones del sistema para usuarios."""

    # Tipos de notificación
    TYPE_GENERAL = 'GEN'
    TYPE_ALARM = 'ALM'
    TYPE_POMODORO = 'POM'
    TYPE_FRIEND_REQUEST = 'FRQ'
    TYPE_STUDY_MILESTONE = 'STM'
    TYPE_ACHIEVEMENT = 'ACH'

    NOTIFICATION_TYPES = [
        (TYPE_GENERAL, _('General')),
        (TYPE_ALARM, _('Alarma')),
        (TYPE_POMODORO, _('Pomodoro')),
        (TYPE_FRIEND_REQUEST, _('Solicitud de amistad')),
        (TYPE_STUDY_MILESTONE, _('Logro de estudio')),
        (TYPE_ACHIEVEMENT, _('Logro desbloqueado')),
    ]

    # Niveles de prioridad
    PRIORITY_LOW = 'L'
    PRIORITY_MEDIUM = 'M'
    PRIORITY_HIGH = 'H'

    PRIORITY_LEVELS = [
        (PRIORITY_LOW, _('Baja')),
        (PRIORITY_MEDIUM, _('Media')),
        (PRIORITY_HIGH, _('Alta')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('usuario'),
    )

    notification_type = models.CharField(
        _('tipo'),
        max_length=3,
        choices=NOTIFICATION_TYPES,
        default=TYPE_GENERAL,
    )

    title = models.CharField(_('título'), max_length=255)
    message = models.TextField(_('mensaje'))

    # Link opcional para redirigir al hacer clic
    link = models.URLField(_('enlace'), max_length=500, blank=True, null=True)

    # Prioridad para determinar estilo visual y comportamiento
    priority = models.CharField(
        _('prioridad'),
        max_length=1,
        choices=PRIORITY_LEVELS,
        default=PRIORITY_MEDIUM,
    )

    # Relación genérica al objeto relacionado (alarma, pomodoro, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('tipo de contenido'),
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    # Control de estado y timestamps
    is_read = models.BooleanField(_('leída'), default=False)
    is_dismissed = models.BooleanField(_('descartada'), default=False)
    created_at = models.DateTimeField(_('creada'), auto_now_add=True)
    read_at = models.DateTimeField(_('leída el'), null=True, blank=True)

    class Meta:
        verbose_name = _('notificación')
        verbose_name_plural = _('notificaciones')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read', 'is_dismissed']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"

    def mark_as_read(self):
        """Marcar la notificación como leída."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def dismiss(self):
        """Descartar la notificación."""
        self.is_dismissed = True
        self.save()

    @property
    def is_recent(self):
        """Determinar si la notificación es reciente (menos de 24h)."""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days < 1
