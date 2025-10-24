from django.contrib import admin
from .models import Subject, Post


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'get_subjects',
        'created_at',
        'likes_count',
        'saves_count',
        'is_public',
    )
    list_filter = ('is_public', 'subjects', 'created_at')
    search_fields = ('user__username', 'caption')
    raw_id_fields = ('user',)
    filter_horizontal = ('subjects', 'likes', 'saved_by')
    readonly_fields = ('likes_count', 'saves_count', 'created_at', 'updated_at')

    def get_subjects(self, obj):
        return ", ".join(s.name for s in obj.subjects.all())
    get_subjects.short_description = 'Asignaturas'

    def likes_count(self, obj):
        return obj.likes_count
    likes_count.short_description = 'Likes'

    def saves_count(self, obj):
        return obj.saves_count
    saves_count.short_description = 'Guardados'
