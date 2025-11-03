from django.urls import path
from .views import ProfileDetailView, MyProfileRedirectView
from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("me/", views.MyProfileRedirectView.as_view(), name="me"),
    path("search/", views.UserSearchView.as_view(), name="search"),
    path("<str:username>/", views.ProfileDetailView.as_view(), name="detail"),
    path("<str:username>/send-request/", views.SendFriendRequestView.as_view(),
         name="send_request"),
]
