from django.urls import path
from .views import (
    PostListView, PostDetailView, UserPostsView,
    PostCreateView, PostUpdateView, PostDeleteView,
    ToggleLikeView, ToggleSaveView,
)

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("create/", PostCreateView.as_view(), name="create"),
    path("user/<str:username>/", UserPostsView.as_view(), name="user_posts"),
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", PostUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="delete"),
    path("<int:pk>/like/", ToggleLikeView.as_view(), name="like"),
    path("<int:pk>/save/", ToggleSaveView.as_view(), name="save"),
]
