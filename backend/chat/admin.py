from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'updated_at', 'get_messages_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__username',)
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at', 'updated_at')

    def get_participants(self, obj):
        return ", ".join(user.username for user in obj.participants.all())
    get_participants.short_description = 'Participantes'

    def get_messages_count(self, obj):
        return obj.messages.count()
    get_messages_count.short_description = 'Mensajes'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'get_conversation', 'short_content', 'created_at', 'is_read')
    list_filter = ('created_at', 'sender', 'conversation')
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('conversation', 'sender')
    filter_horizontal = ('read_by',)
    readonly_fields = ('created_at',)

    def get_conversation(self, obj):
        return f"Chat {obj.conversation.id}: {obj.conversation}"
    get_conversation.short_description = 'Conversación'

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = 'Contenido'
