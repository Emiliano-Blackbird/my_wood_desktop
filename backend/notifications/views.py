from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Lista de notificaciones del usuario."""
    model = Notification
    template_name = "notifications/inbox.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return (
            Notification.objects.filter(user=self.request.user)
            .select_related('user')
            .order_by('-created_at')
        )


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una notificación."""
    model = Notification
    template_name = "notifications/detail.html"
    context_object_name = "notification"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Marcar como leída al verla
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save(update_fields=['is_read'])
        return response


class MarkAsReadView(LoginRequiredMixin, View):
    """Marca una notificación como leída (AJAX)."""
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification,
            pk=self.kwargs['pk'],
            user=request.user
        )
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return JsonResponse({'ok': True, 'id': notification.pk})


class MarkAllReadView(LoginRequiredMixin, View):
    """Marca todas las notificaciones como leídas."""
    def post(self, request, *args, **kwargs):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return JsonResponse({'ok': True, 'marked': count})
