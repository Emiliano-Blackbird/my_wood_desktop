from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Conversation(models.Model):
    """Conversación entre dos usuarios."""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name=_('participantes'),
    )
    created_at = models.DateTimeField(
        _('creada'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('actualizada'),
        auto_now=True,
    )

    class Meta:
        verbose_name = _('conversación')
        verbose_name_plural = _('conversaciones')
        ordering = ['-updated_at']

    def __str__(self):
        participants = self.participants.all()
        if participants.exists():
            return f"Chat: {' & '.join(user.username for user in participants)}"
        return f"Conversación {self.id}"


class Message(models.Model):
    """Mensaje individual en una conversación."""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversación'),
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('emisor'),
    )
    content = models.TextField(_('contenido'))
    created_at = models.DateTimeField(
        _('enviado'),
        auto_now_add=True,
    )
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_messages',
        verbose_name=_('leído por'),
        blank=True,
    )

    class Meta:
        verbose_name = _('mensaje')
        verbose_name_plural = _('mensajes')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

    def mark_as_read(self, user):
        """Marcar mensaje como leído por un usuario."""
        if user != self.sender:
            self.read_by.add(user)

    @property
    def is_read(self):
        """Verificar si el mensaje ha sido leído por todos los participantes."""
        participants = self.conversation.participants.exclude(id=self.sender.id)
        return all(user in self.read_by.all() for user in participants)
