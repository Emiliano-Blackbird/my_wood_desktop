from django.contrib import admin
from django.urls import path, include
from .views import (
    HomeView,
    LoginView,
    RegisterView,
    DashboardView,
    LegalView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('legal/', LegalView.as_view(), name='legal'),
    path('profiles/', include('profiles.urls', namespace='profiles')),
]
