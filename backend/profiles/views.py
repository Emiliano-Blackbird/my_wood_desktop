# ...existing code...
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class ProfileDetailView(DetailView):
    model = User
    template_name = "profiles/detail.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_obj = self.get_object()
        profile = getattr(user_obj, "profile", None)
        # preparar listas seguras para template
        achievements = []
        subjects = []
        try:
            if profile is not None and hasattr(profile, "achievements"):
                achievements = list(profile.achievements.all())
        except Exception:
            achievements = []
        try:
            if profile is not None and hasattr(profile, "current_subjects"):
                subjects = list(profile.current_subjects.all())
        except Exception:
            subjects = []
        # determinar si el usuario actual puede enviar friend request
        can_send_request = (
            self.request.user.is_authenticated
            and self.request.user != user_obj
        )
        ctx.update(
            {
                "profile": profile,
                "achievements": achievements,
                "current_subjects": subjects,
                "can_send_request": can_send_request,
            }
        )
        return ctx


class MyProfileRedirectView(LoginRequiredMixin, View):
    """Redirige a la página de perfil del usuario logueado."""
    def get(self, request, *args, **kwargs):
        return redirect(reverse("profiles:detail", args=[request.user.username]))


class UserSearchView(LoginRequiredMixin, ListView):
    model = User
    template_name = "profiles/search_results.html"
    context_object_name = "results"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return User.objects.none()
        return User.objects.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
        ).exclude(pk=self.request.user.pk)[:50]


class SendFriendRequestView(LoginRequiredMixin, View):
    """Crear friend request desde perfil público (POST)."""

    def post(self, request, username, *args, **kwargs):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            messages.error(request, "No puedes enviarte una solicitud a ti mismo.")
            return redirect(reverse("profiles:detail", args=[username]))

        # intentar usar el modelo FriendRequest si existe
        try:
            from .models import FriendRequest
        except Exception:
            FriendRequest = None

        if FriendRequest is None:
            messages.error(request, "Funcionalidad de friend request no disponible.")
            return redirect(reverse("profiles:detail", args=[username]))

        # evitar duplicados
        exists = FriendRequest.objects.filter(
            from_user=request.user, to_user=target
        ).exists()
        if exists:
            messages.info(request, "Ya enviaste una solicitud a este usuario.")
            return redirect(reverse("profiles:detail", args=[username]))

        try:
            FriendRequest.objects.create(from_user=request.user, to_user=target)
            messages.success(request, "Solicitud enviada.")
        except IntegrityError:
            messages.error(request, "No se pudo enviar la solicitud.")
        except Exception:
            messages.error(request, "Ocurrió un error al enviar la solicitud.")
        return redirect(reverse("profiles:detail", args=[username]))
