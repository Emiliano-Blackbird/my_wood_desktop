from django.apps import AppConfig


class StudyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'study'

    def ready(self):
        # importa el módulo de signals para registrar handlers (create PomodoroSettings, etc.)
        import study.signals
