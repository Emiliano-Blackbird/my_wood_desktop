from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'notification_type',
        'priority',
        'created_at',
        'is_read',
        'is_dismissed',
        'is_recent',
    )

    list_filter = (
        'notification_type',
        'priority',
        'is_read',
        'is_dismissed',
        'created_at',
        ('user', admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        'title',
        'message',
        'user__username',
        'user__email',
    )

    readonly_fields = (
        'created_at',
        'read_at',
    )

    date_hierarchy = 'created_at'

    ordering = ('-created_at',)

    actions = ['mark_as_read', 'mark_as_unread', 'dismiss_notifications']

    def mark_as_read(self, request, queryset):
        updated = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        self.message_user(
            request,
            _(f'Se marcaron {updated} notificaciones como leídas.')
        )
    mark_as_read.short_description = _('Marcar como leídas')

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(
            request,
            _(f'Se marcaron {updated} notificaciones como no leídas.')
        )
    mark_as_unread.short_description = _('Marcar como no leídas')

    def dismiss_notifications(self, request, queryset):
        updated = queryset.update(is_dismissed=True)
        self.message_user(
            request,
            _(f'Se descartaron {updated} notificaciones.')
        )
    dismiss_notifications.short_description = _('Descartar notificaciones')

    def is_recent(self, obj):
        return obj.is_recent
    is_recent.boolean = True
    is_recent.short_description = _('Reciente')
