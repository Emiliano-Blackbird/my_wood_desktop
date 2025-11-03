# ...existing code...
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.db import transaction
from .models import Conversation, Message
from django.contrib import messages

User = get_user_model()


class ConversationListView(LoginRequiredMixin, ListView):
    """Listado de conversaciones del usuario."""
    model = Conversation
    template_name = "chat/list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        qs = (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related(
                "participants", "messages__sender", "messages__read_by"
            )
            .order_by("-updated_at")
        )
        # Forzar evaluación y añadir atributos útiles para la plantilla
        convs = list(qs)
        for conv in convs:
            try:
                conv.unread_count = conv.messages.exclude(
                    read_by=self.request.user
                ).count()
            except Exception:
                conv.unread_count = 0
        return convs


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra los mensajes de una conversación.
    Permite enviar mensajes vía POST (form simple) o AJAX.
    """
    model = Conversation
    template_name = "chat/detail.html"
    context_object_name = "conversation"

    def get_object(self, queryset=None):
        conv = super().get_object(queryset)
        if not conv.participants.filter(pk=self.request.user.pk).exists():
            raise HttpResponseForbidden("No tienes acceso a esta conversación")
        return conv

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            msgs_qs = (
                self.object.messages.select_related("sender")
                .order_by("created_at")
            )
            msgs = list(msgs_qs)
            # añadir atributo 'text' seguro para la plantilla
            for m in msgs:
                m.text = getattr(m, "content", None) or getattr(m, "body", None) or ""
            ctx["messages"] = msgs
        except Exception:
            ctx["messages"] = []
        return ctx

    def post(self, request, *args, **kwargs):
        """Enviar un mensaje (form submit o AJAX). Acepta 'content' o 'body' del form."""
        conv = self.get_object()
        content = (request.POST.get("content") or request.POST.get("body") or "").strip()
        if not content:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "error": "Contenido vacío"}, status=400)
            return redirect(conv.get_absolute_url() if hasattr(conv, "get_absolute_url") else reverse("chat:detail", args=[conv.pk]))

        # Crear mensaje (campo 'content' es el estándar en tu modelo)
        try:
            msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        except Exception:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "error": "No se pudo crear el mensaje"}, status=500)
            return redirect(conv.get_absolute_url() if hasattr(conv, "get_absolute_url") else reverse("chat:detail", args=[conv.pk]))

        # marcar como leído por el remitente (si existe la relación read_by)
        try:
            msg.read_by.add(request.user)
        except Exception:
            pass

        # actualizar updated_at de la conversación si procede (seguridad adicional)
        try:
            timestamp = getattr(msg, "created_at", None)
            if timestamp is not None:
                Conversation.objects.filter(pk=conv.pk).update(updated_at=timestamp)
        except Exception:
            pass

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "ok": True,
                "message": {
                    "id": msg.pk,
                    "sender": request.user.username,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if getattr(msg, "created_at", None) else None,
                }
            })
        return redirect(conv.get_absolute_url() if hasattr(conv, "get_absolute_url") else reverse("chat:detail", args=[conv.pk]))


class ConversationDeleteView(LoginRequiredMixin, View):
    """Eliminar una conversación (solo participantes)."""
    def post(self, request, pk, *args, **kwargs):
        conv = get_object_or_404(Conversation, pk=pk)
        if not conv.participants.filter(pk=request.user.pk).exists():
            return HttpResponseForbidden("No autorizado")

        try:
            with transaction.atomic():
                conv.delete()
                messages.success(request, "Conversación eliminada.")
        except Exception:
            messages.error(request, "No se pudo eliminar la conversación.")
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "error": "delete_failed"}, status=500)
            return redirect(reverse("chat:list"))

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "redirect": reverse("chat:list")})
        return redirect(reverse("chat:list"))


class StartConversationView(LoginRequiredMixin, View):
    """
    Inicia una conversación entre el usuario y otro usuario.
    Si ya existe, devuelve la existente.
    Espera 'user_id' (POST) o 'username' (POST).
    Responde JSON (útil para frontend JS).
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

        # Buscar conversación existente entre los dos
        conv = (
            Conversation.objects.filter(participants=request.user)
            .filter(participants=other)
            .distinct()
            .first()
        )

        if conv:
            return JsonResponse({"ok": True, "conversation_id": conv.pk, "url": reverse("chat:detail", args=[conv.pk])})

        # Crear nueva conversación con transacción
        try:
            with transaction.atomic():
                conv = Conversation.objects.create()
                conv.participants.add(request.user, other)
        except Exception:
            return JsonResponse({"ok": False, "error": "No se pudo crear la conversación"}, status=500)

        return JsonResponse({"ok": True, "conversation_id": conv.pk, "url": reverse("chat:detail", args=[conv.pk])})


class MarkConversationReadView(LoginRequiredMixin, View):
    """
    Marca todos los mensajes de una conversación como leídos por el usuario.
    """
    def post(self, request, *args, **kwargs):
        conv_id = request.POST.get("conversation_id")
        conv = get_object_or_404(Conversation, pk=conv_id)
        if not conv.participants.filter(pk=request.user.pk).exists():
            return JsonResponse({"ok": False, "error": "No autorizado"}, status=403)

        unread_messages = conv.messages.exclude(read_by=request.user)
        count = 0
        for msg in unread_messages:
            msg.read_by.add(request.user)
            count += 1
        return JsonResponse({"ok": True, "marked": count})
