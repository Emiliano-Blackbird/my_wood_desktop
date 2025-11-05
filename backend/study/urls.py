from django.urls import path
from .views import (
    StartSessionView,
    EndSessionView,
    SessionListView,
    PomodoroView,
    SubjectCreateView,
)

app_name = "study"

urlpatterns = [
    path("", SessionListView.as_view(), name="list"),
    path("start/", StartSessionView.as_view(), name="start_session"),
    path("end/<int:pk>/", EndSessionView.as_view(), name="end_session"),
    path("pomodoro/", PomodoroView.as_view(), name="pomodoro"),
    path("subject/create/", SubjectCreateView.as_view(), name="subject_create"),
]
