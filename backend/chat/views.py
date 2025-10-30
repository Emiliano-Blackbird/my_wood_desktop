from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Conversation, Message

User = get_user_model()


class ConversationListView(LoginRequiredMixin, ListView):
    """Listado de conversaciones del usuario."""
    model = Conversation
    template_name = "chat/conversation_list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related("participants")
            .order_by("-updated_at")
        )


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra los mensajes de una conversación.
    Permite enviar mensajes vía POST (form simple) o AJAX.
    """
    model = Conversation
    template_name = "chat/conversation_detail.html"
    context_object_name = "conversation"

    def get_object(self, queryset=None):
        conv = super().get_object(queryset)
        if not conv.participants.filter(pk=self.request.user.pk).exists():
            raise HttpResponseForbidden("No tienes acceso a esta conversación.")
        return conv

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # traer mensajes ordenados y limitar si es necesario
        ctx["messages"] = self.object.messages.select_related("sender").order_by("created_at")
        return ctx

    def post(self, request, *args, **kwargs):
        """Enviar un mensaje (form submit o AJAX)."""
        conv = self.get_object()
        content = request.POST.get("content", "").strip()
        if not content:
            if request.is_ajax():
                return JsonResponse({"ok": False, "error": "Contenido vacío"}, status=400)
            return redirect(conv.get_absolute_url() if hasattr(conv, "get_absolute_url") else reverse("chat:detail", args=[conv.pk]))

        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        # marcar como leído por el remitente
        msg.read_by.add(request.user)
        # actualizar la conversación (si usas updated_at en el modelo)
        Conversation.objects.filter(pk=conv.pk).update(updated_at=msg.created_at)

        if request.is_ajax():
            return JsonResponse({
                "ok": True,
                "message": {
                    "id": msg.pk,
                    "sender": request.user.username,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
            })
        return redirect(conv.get_absolute_url() if hasattr(conv, "get_absolute_url") else reverse("chat:detail", args=[conv.pk]))


class StartConversationView(LoginRequiredMixin, View):
    """
    Inicia una conversación entre el usuario y otro usuario.
    Si ya existe, redirige a la existente.
    Espera 'user_id' (POST) o 'username' (GET/POST).
    """
    def post(self, request, *args, **kwargs):
        other_id = request.POST.get("user_id")
        other_username = request.POST.get("username")
        other = None

        if other_id:
            other = get_object_or_404(User, pk=other_id)
        elif other_username:
            other = get_object_or_404(User, username=other_username)
        else:
            return JsonResponse({"ok": False, "error": "user_id o username requerido"}, status=400)

        if other == request.user:
            return JsonResponse({"ok": False, "error": "No puedes iniciar conversación contigo mismo."}, status=400)

        # buscar conversación existente entre los dos
        conv = (
            Conversation.objects.filter(participants=request.user)
            .filter(participants=other)
            .distinct()
            .first()
        )

        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, other)
            conv.save()

        return JsonResponse({"ok": True, "conversation_id": conv.pk, "url": reverse("chat:detail", args=[conv.pk])})


class MarkConversationReadView(LoginRequiredMixin, View):
    """
    Marca todos los mensajes de una conversación como leídos por el usuario.
    Útil para llamadas AJAX desde el cliente al abrir la conversación.
    """
    def post(self, request, *args, **kwargs):
        conv_id = request.POST.get("conversation_id")
        conv = get_object_or_404(Conversation, pk=conv_id)
        if not conv.participants.filter(pk=request.user.pk).exists():
            return JsonResponse({"ok": False, "error": "No autorizado"}, status=403)

        unread_messages = conv.messages.exclude(read_by=request.user)
        for msg in unread_messages:
            msg.read_by.add(request.user)
        return JsonResponse({"ok": True, "marked": unread_messages.count()})
