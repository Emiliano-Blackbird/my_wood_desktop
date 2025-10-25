from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Alarm, PomodoroSettings, PostIt, StudySession


@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'time', 'get_days', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'user__username')
    ordering = ('time',)

    def get_days(self, obj):
        days_map = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        return ', '.join(days_map[day] for day in obj.days)
    get_days.short_description = _('Días')


@admin.register(PomodoroSettings)
class PomodoroSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'work_duration',
        'break_duration',
        'long_break_duration',
        'sessions_until_long_break',
    )
    search_fields = ('user__username',)


@admin.register(PostIt)
class PostItAdmin(admin.ModelAdmin):
    list_display = (
        'short_content',
        'user',
        'color',
        'position_x',
        'position_y',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at', 'color')
    search_fields = ('content', 'user__username')
    ordering = ('-updated_at',)

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = _('Contenido')


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subject',
        'start_time',
        'end_time',
        'get_duration',
        'is_active',
    )
    list_filter = (
        'subject',
        'start_time',
        'end_time',
        ('user', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'user__username',
        'subject__name',
        'notes',
    )
    readonly_fields = ('duration',)
    ordering = ('-start_time',)
    date_hierarchy = 'start_time'

    def get_duration(self, obj):
        if obj.duration:
            hours = obj.duration.total_seconds() / 3600
            return f"{hours:.1f} horas"
        return "En curso" if obj.is_active else "-"
    get_duration.short_description = _('Duración')

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = _('Activa')

    actions = ['end_selected_sessions']

    def end_selected_sessions(self, request, queryset):
        active_sessions = queryset.filter(end_time__isnull=True)
        for session in active_sessions:
            session.end_session()
        self.message_user(
            request,
            f"Se finalizaron {active_sessions.count()} sesiones de estudio."
        )
    end_selected_sessions.short_description = _("Finalizar sesiones seleccionadas")
