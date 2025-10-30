from django.urls import path
from . import views

app_name = 'chat'  # Esto define el namespace 'chat'

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='list'),
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='detail'),
    path('start/', views.StartConversationView.as_view(), name='start'),
    path('read/', views.MarkConversationReadView.as_view(), name='mark_read'),
]
