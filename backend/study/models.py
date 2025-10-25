from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Alarm(models.Model):
    """Alarmas configurables para el usuario."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alarms',
        verbose_name=_('usuario'),
    )
    name = models.CharField(
        _('nombre'),
        max_length=100,
        help_text=_('Nombre de la alarma'),
    )
    time = models.TimeField(_('hora'))
    days = models.JSONField(
        _('días'),
        default=list,
        help_text=_('Lista de días de la semana (0-6, 0=Lunes)'),
    )
    is_active = models.BooleanField(_('activa'), default=True)
    created_at = models.DateTimeField(_('creada'), auto_now_add=True)

    class Meta:
        verbose_name = _('alarma')
        verbose_name_plural = _('alarmas')
        ordering = ['time']

    def __str__(self):
        return f"{self.name} - {self.time}"


class PomodoroSettings(models.Model):
    """Configuración personal de pomodoro para cada usuario."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pomodoro_settings',
        verbose_name=_('usuario'),
    )
    work_duration = models.PositiveIntegerField(
        _('duración trabajo'),
        default=25,
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text=_('Duración del período de trabajo en minutos'),
    )
    break_duration = models.PositiveIntegerField(
        _('duración descanso'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        help_text=_('Duración del período de descanso en minutos'),
    )
    long_break_duration = models.PositiveIntegerField(
        _('duración descanso largo'),
        default=15,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text=_('Duración del descanso largo en minutos'),
    )
    sessions_until_long_break = models.PositiveIntegerField(
        _('sesiones hasta descanso largo'),
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        verbose_name = _('configuración pomodoro')
        verbose_name_plural = _('configuraciones pomodoro')

    def __str__(self):
        return f"Pomodoro config: {self.user.username}"


class PostIt(models.Model):
    """Notas rápidas tipo post-it para el escritorio."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='postits',
        verbose_name=_('usuario'),
    )
    content = models.TextField(_('contenido'), max_length=500)
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#ffeb3b',
        help_text=_('Color en formato hex (#ffeb3b)'),
    )
    position_x = models.IntegerField(_('posición X'), default=0)
    position_y = models.IntegerField(_('posición Y'), default=0)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('post-it')
        verbose_name_plural = _('post-its')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.content[:30]}..."


class StudySession(models.Model):
    """Registro de sesiones de estudio por asignatura."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_sessions',
        verbose_name=_('usuario'),
    )
    subject = models.ForeignKey(
        'posts.Subject',  # referencia a Subject del app posts
        on_delete=models.CASCADE,
        related_name='study_sessions',
        verbose_name=_('asignatura'),
    )
    start_time = models.DateTimeField(_('inicio'))
    end_time = models.DateTimeField(_('fin'), null=True, blank=True)
    duration = models.DurationField(
        _('duración'),
        null=True,
        blank=True,
        help_text=_('Duración total de la sesión'),
    )
    notes = models.TextField(
        _('notas'),
        blank=True,
        help_text=_('Notas o comentarios sobre la sesión'),
    )

    class Meta:
        verbose_name = _('sesión de estudio')
        verbose_name_plural = _('sesiones de estudio')
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'subject', 'start_time']),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.start_time.date()}"

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.end_time is None

    def end_session(self):
        if self.is_active:
            self.end_time = timezone.now()
            self.save()
