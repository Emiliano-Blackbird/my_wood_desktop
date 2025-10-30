from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='inbox'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='detail'),
    path('<int:pk>/mark-read/', views.MarkAsReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]
