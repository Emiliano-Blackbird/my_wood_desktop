from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Post, Subject


class PostListView(ListView):
    model = Post
    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        qs = Post.objects.select_related('user').prefetch_related('subjects')
        # Show only public posts by default; allow owner to see their private posts on profile feed
        return qs.filter(is_public=True)


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/detail.html"
    context_object_name = "post"


class UserPostsView(ListView):
    model = Post
    template_name = "posts/user_posts.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        username = self.kwargs.get("username")
        return Post.objects.filter(user__username=username).select_related('user').prefetch_related('subjects')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ("subjects", "image", "caption", "is_public")
    template_name = "posts/form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        resp = super().form_valid(form)
        messages.success(self.request, "Post publicado.")
        return resp

    def get_success_url(self):
        return reverse("posts:detail", args=[self.object.pk])


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ("subjects", "image", "caption", "is_public")
    template_name = "posts/form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Post actualizado.")
        return resp

    def get_success_url(self):
        return reverse("posts:detail", args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "posts/confirm_delete.html"
    success_url = reverse_lazy("posts:list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Post eliminado.")
        return super().delete(request, *args, **kwargs)


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        liked = post.toggle_like(request.user)
        return redirect(request.META.get("HTTP_REFERER") or reverse("posts:detail", args=[pk]))


class ToggleSaveView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        if post.is_saved_by(request.user):
            post.unsave_for(request.user)
        else:
            post.save_for(request.user)
        return redirect(request.META.get("HTTP_REFERER") or reverse("posts:detail", args=[pk]))
