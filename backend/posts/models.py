from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    """Asignatura / tag de la materia (para etiquetar posts)."""
    name = models.CharField(_('nombre'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True)

    class Meta:
        verbose_name = _('asignatura')
        verbose_name_plural = _('asignaturas')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Post(models.Model):
    """Contenido compartido por usuarios: img + tags de asignatura."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('usuario'),
    )
    subjects = models.ManyToManyField(
        Subject,
        blank=True,
        related_name='posts',
        verbose_name=_('asignaturas'),
        help_text=_('Etiquetas de las asignaturas relacionadas con el post.'),
    )
    image = models.ImageField(
        _('imagen'),
        upload_to='posts/images/',
        null=True,
        blank=True,
        help_text=_('Imagen, esquema o captura (opcional).'),
    )
    caption = models.TextField(
        _('caption'),
        max_length=1000,
        blank=True,
        help_text=_('Breve descripción o contexto del resumen.'),
    )
    created_at = models.DateTimeField(
        _('creado el'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('actualizado el'),
        auto_now=True,
    )

    # Usuarios que dieron "like" (para relevancia/recomendación)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_posts',
        verbose_name=_('likes'),
    )

    # Usuarios que guardaron el post (bookmark)
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='saved_posts',
        verbose_name=_('guardado por'),
    )

    is_public = models.BooleanField(
        _('público'),
        default=True,
        help_text=_('Si es False, el post sólo será visible para el autor o seguidores si la lógica lo permite.'),
    )

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        snippet = (self.caption[:40] + '...') if self.caption and len(self.caption) > 43 else (self.caption or f'Post {self.pk}')
        return f'{self.user.username}: {snippet}'

    # Contadores y utilidades
    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def saves_count(self):
        return self.saved_by.count()

    def is_liked_by(self, user):
        if not user or user.is_anonymous:
            return False
        return self.likes.filter(pk=user.pk).exists()

    def like(self, user):
        if not user or user.is_anonymous:
            return False
        self.likes.add(user)
        return True

    def unlike(self, user):
        if not user or user.is_anonymous:
            return False
        self.likes.remove(user)
        return True

    def toggle_like(self, user):
        if self.is_liked_by(user):
            self.unlike(user)
            return False
        self.like(user)
        return True

    def is_saved_by(self, user):
        if not user or user.is_anonymous:
            return False
        return self.saved_by.filter(pk=user.pk).exists()

    def save_for(self, user):
        if not user or user.is_anonymous:
            return False
        self.saved_by.add(user)
        return True

    def unsave_for(self, user):
        if not user or user.is_anonymous:
            return False
        self.saved_by.remove(user)
        return True

    def relevance_score(self, likes_weight=1.0, saves_weight=1.5):
        """
        Simple scoring: combinar likes y guardados para recomendar.
        Ajusta pesos según necesidad.
        """
        return self.likes_count * likes_weight + self.saves_count * saves_weight
