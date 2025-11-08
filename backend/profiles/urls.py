from django.urls import path
from .views import ProfileDetailView, MyProfileRedirectView, UserSearchView, ProfileUpdateView, SendFriendRequestView
from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("me/", views.MyProfileRedirectView.as_view(), name="me"),
    path("search/", views.UserSearchView.as_view(), name="search"),
    path('edit/', ProfileUpdateView.as_view(), name='edit'),
    path('<str:username>/', ProfileDetailView.as_view(), name='detail'),
    path('<str:username>/friend-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
]
