from datetime import datetime


def navigation_counts(request):
    """Context processor para contadores en el header."""
    if not request.user.is_authenticated:
        return {}

    # Inicializar contadores
    unread_messages = 0
    unread_notifications = 0

    try:
        if hasattr(request.user, 'received_messages'):
            unread_messages = request.user.received_messages.filter(is_read=False).count()
        elif hasattr(request.user, 'read_messages'):
            unread_messages = request.user.read_messages.filter(is_read=False).count()
        elif hasattr(request.user, 'messages'):
            unread_messages = request.user.messages.filter(is_read=False).count()
    except Exception:
        pass

    # Notificaciones no leídas
    try:
        if hasattr(request.user, 'notifications'):
            unread_notifications = request.user.notifications.filter(is_read=False).count()
    except Exception:
        pass

    return {
        'unread_messages_count': unread_messages,
        'unread_notifications_count': unread_notifications,
    }


def site_info(request):
    """Context processor para información general del sitio."""
    return {
        'current_year': datetime.now().year,
        'site_name': 'My Wood Desk',
    }
