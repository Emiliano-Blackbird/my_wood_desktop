from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

# import simple y silencioso (si no existe, lo manejamos)
try:
    from .models import FriendRequest
except Exception:
    FriendRequest = None


class ProfileDetailView(DetailView):
    model = User
    template_name = "profiles/detail.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_obj = self.get_object()
        profile = getattr(user_obj, "profile", None)

        ctx["profile"] = profile
        ctx["achievements"] = list(profile.achievements.all()) if profile and hasattr(profile, "achievements") else []
        ctx["current_subjects"] = list(profile.current_subjects.all()) if profile and hasattr(profile, "current_subjects") else []

        # Conteo de amigos sencillo: usar m2m profile.friends si existe,
        # si no, intentar obtener desde FriendRequest (accepted=True).
        friends = []
        if profile and hasattr(profile, "friends"):
            try:
                friends = list(profile.friends.all())
            except Exception:
                friends = []
        elif FriendRequest is not None:
            try:
                accepted = FriendRequest.objects.filter(
                    Q(from_user=user_obj) | Q(to_user=user_obj),
                    accepted=True
                )
                for fr in accepted:
                    friends.append(fr.to_user if fr.from_user == user_obj else fr.from_user)
            except Exception:
                friends = []

        ctx["friends_list"] = friends
        ctx["friends_count"] = len(friends)
        ctx["can_send_request"] = self.request.user.is_authenticated and self.request.user != user_obj
        return ctx


class UserSearchView(LoginRequiredMixin, ListView):
    model = User
    template_name = "profiles/search_results.html"
    context_object_name = "results"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return User.objects.none()
        return User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).exclude(pk=self.request.user.pk)[:50]


class SendFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, username, *args, **kwargs):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            messages.error(request, "No puedes enviarte una solicitud a ti mismo.")
            return redirect(reverse("profiles:detail", args=[username]))

        if FriendRequest is None:
            messages.error(request, "Funcionalidad de friend request no disponible.")
            return redirect(reverse("profiles:detail", args=[username]))

        # Chequeo simple de duplicados y creación
        if FriendRequest.objects.filter(from_user=request.user, to_user=target).exists():
            messages.info(request, "Ya enviaste una solicitud a este usuario.")
            return redirect(reverse("profiles:detail", args=[username]))

        try:
            FriendRequest.objects.create(from_user=request.user, to_user=target)
            messages.success(request, "Solicitud enviada.")
        except Exception:
            messages.error(request, "No se pudo enviar la solicitud.")
        return redirect(reverse("profiles:detail", args=[username]))


class MyProfileRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect(reverse("profiles:detail", args=[request.user.username]))