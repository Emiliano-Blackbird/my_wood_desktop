from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from django.db import transaction

from .models import StudySession, Subject
from .forms import SubjectForm


class StartSessionView(LoginRequiredMixin, View):
    """Inicia una nueva sesión de estudio. GET muestra formulario; POST crea la sesión."""
    def get(self, request):
        subjects = Subject.objects.filter(user=request.user) if Subject is not None else Subject.objects.none()
        if not subjects:
            messages.warning(request, "No hay asignaturas. Crea una asignatura antes de iniciar una sesión.")
        return render(request, "study/start.html", {"subjects": subjects})

    def post(self, request):
        subject_id = request.POST.get("subject")
        if not subject_id:
            messages.error(request, "Selecciona una asignatura para iniciar la sesión.")
            return redirect("study:start_session")

        subject = get_object_or_404(Subject, pk=subject_id, user=request.user)

        with transaction.atomic():
            session = StudySession.objects.create(
                user=request.user,
                start_time=timezone.now(),
                subject=subject
            )
        messages.success(request, "Sesión iniciada.")
        return redirect("dashboard")


class EndSessionView(LoginRequiredMixin, View):
    """Marca la sesión como finalizada (set end_time)."""
    def post(self, request, pk):
        session = get_object_or_404(StudySession, pk=pk, user=request.user)
        if session.end_time is None:
            session.end_time = timezone.now()
            session.save(update_fields=["end_time", "duration"])
        return redirect("dashboard")


class SessionListView(LoginRequiredMixin, ListView):
    """Listado de sesiones del usuario."""
    template_name = "study/list.html"
    context_object_name = "sessions"
    paginate_by = 20

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user).select_related('subject').order_by("-start_time")


class PomodoroView(LoginRequiredMixin, TemplateView):
    """Vista estática / JS para el temporizador Pomodoro."""
    template_name = "study/pomodoro.html"


class AjaxEndSessionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(StudySession, pk=pk, user=request.user)
        session.end_time = timezone.now()
        session.save(update_fields=["end_time", "duration"])
        return JsonResponse({"id": session.pk, "ended_at": session.end_time.isoformat()})


class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "study/subject_form.html"
    success_url = reverse_lazy("study:start_session")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)