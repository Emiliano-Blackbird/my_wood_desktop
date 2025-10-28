from django.urls import path
from .views import ProfileDetailView, MyProfileRedirectView

app_name = 'profiles'

urlpatterns = [
    path('me/', MyProfileRedirectView.as_view(), name='me'),
    path('<str:username>/', ProfileDetailView.as_view(), name='detail'),
]
