from django.contrib import admin
from profiles.models import UserProfile, FriendRequest


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'bio', 'get_friends_count', 'get_followers_count')
    list_filter = ('user__is_active', 'user__date_joined')
    search_fields = ('user__username', 'user__email', 'bio')
    filter_horizontal = ('friends', 'following')
    readonly_fields = ('get_friends_count', 'get_followers_count')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_friends_count(self, obj):
        return obj.friends.count()
    get_friends_count.short_description = 'Amigos'

    def get_followers_count(self, obj):
        return obj.followers.count()
    get_followers_count.short_description = 'Seguidores'


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at', 'responded_at')
    search_fields = (
        'from_user__user__username',
        'to_user__user__username',
    )
    readonly_fields = ('created_at', 'responded_at')
    actions = ['accept_requests', 'reject_requests']

    def accept_requests(self, request, queryset):
        for friend_request in queryset.filter(status=FriendRequest.STATUS_PENDING):
            friend_request.accept()
    accept_requests.short_description = "Aceptar solicitudes seleccionadas"

    def reject_requests(self, request, queryset):
        for friend_request in queryset.filter(status=FriendRequest.STATUS_PENDING):
            friend_request.reject()
    reject_requests.short_description = "Rechazar solicitudes seleccionadas"
