from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, TemplateView
from django.utils import timezone
from django.http import HttpResponseBadRequest, JsonResponse

# Intentar importar el modelo StudySession
try:
    from study.models import StudySession
except Exception:
    StudySession = None


class StartSessionView(LoginRequiredMixin, View):
    """Inicia una nueva sesión de estudio. POST crea la sesión y redirige al dashboard."""
    def get(self, request):
        # Mostrar un pequeño form si necesitas (opcional)
        return render(request, "study/start.html", {})

    def post(self, request):
        if StudySession is None:
            return HttpResponseBadRequest("StudySession model not available.")
        subject_id = request.POST.get("subject")  # opcional
        session = StudySession.objects.create(
            user=request.user,
            start_time=timezone.now(),
            subject_id=subject_id if subject_id else None
        )
        return redirect("dashboard")


class EndSessionView(LoginRequiredMixin, View):
    """Marca la sesión como finalizada (set end_time)."""
    def post(self, request, pk):
        if StudySession is None:
            return HttpResponseBadRequest("StudySession model not available.")
        session = get_object_or_404(StudySession, pk=pk, user=request.user)
        if session.end_time is None:
            session.end_time = timezone.now()
            session.save(update_fields=["end_time"])
        return redirect("dashboard")


class SessionListView(LoginRequiredMixin, ListView):
    """Listado de sesiones del usuario."""
    template_name = "study/list.html"
    context_object_name = "sessions"
    paginate_by = 20

    def get_queryset(self):
        if StudySession is None:
            return StudySession.objects.none() if StudySession else []
        return StudySession.objects.filter(user=self.request.user).order_by("-start_time")


class PomodoroView(LoginRequiredMixin, TemplateView):
    """Vista estática / JS para el temporizador Pomodoro."""
    template_name = "study/pomodoro.html"


class AjaxEndSessionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if StudySession is None:
            return JsonResponse({"error": "StudySession model not available."}, status=400)
        session = get_object_or_404(StudySession, pk=pk, user=request.user)
        session.end_time = timezone.now()
        session.save()
        return JsonResponse({"id": session.pk, "ended_at": session.end_time.isoformat()})
