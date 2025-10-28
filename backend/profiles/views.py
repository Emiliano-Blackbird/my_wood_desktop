from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, RedirectView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import UserProfile


class ProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'

    # username en la url: /profiles/<username>/
    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(UserProfile, user__username=username)


class MyProfileRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirige /profiles/me/ -> /profiles/<username>/
    útil para enlaces "Mi perfil".
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profiles:detail', args=[self.request.user.username])
