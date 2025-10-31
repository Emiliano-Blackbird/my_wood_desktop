from django.views.generic import TemplateView, CreateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from .forms import LoginForm, RegisterForm

"""
Vistas del proyecto "my_wood_desk_back":
- HomeView: Página de inicio pública.
- LegalView: Página de términos y condiciones.
- LoginView: Wrapper sobre la vista de login de Django.
- LogoutView: Logout simple.
- RegisterView: Registro de usuarios con validación de email.
- DashboardView: Panel principal del usuario con widgets básicos.
"""


class HomeView(TemplateView):
    """Página de inicio pública."""
    template_name = "general/home.html"


class LegalView(TemplateView):
    template_name = "general/legal.html"


class LoginView(View):
    template_name = 'general/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Manejar "Recordarme"
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Expira al cerrar navegador

            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')

            # Redirigir a 'next' o dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
            return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """Cierre de sesión del usuario."""
    def get(self, request):
        logout(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
        return redirect('home')

    def post(self, request):
        logout(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
        return redirect('home')


class RegisterView(CreateView):
    """
    Registro de usuarios con validación de email.
    """
    template_name = "general/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'¡Cuenta creada exitosamente! Ya puedes iniciar sesión como {self.object.username}.'
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Panel principal del usuario.
    Aquí se agregan los widgets principales: resumen de study sessions,
    notificaciones recientes, accesos rápidos (pomodoro, reloj, post-its).
    Vista ligera; la lógica compleja debe residir en servicios
    o managers consultados desde get_context_data.
    """
    template_name = "general/dashboard.html"
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # Intentar añadir perfil si existe (signals suelen crearlo)
        try:
            profile = user.profile
        except Exception:
            profile = None
        ctx['profile'] = profile

        # Placeholders: sustituir por consultas optimizadas según necesidad.
        ctx['recent_notifications'] = getattr(user, 'notifications', None)
        ctx['recent_posts'] = getattr(user, 'posts', None)

        # Ejemplo: estado de sesión de estudio activo (si existe app study)
        # from study.models import StudySession  # import local si se necesita
        # ctx['active_session'] = StudySession.objects.filter(
        #     user=user, end_time__isnull=True
        # ).first()

        return ctx
