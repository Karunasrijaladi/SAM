from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/chat/', views.chat, name='chat'),
    path('api/analyze/', views.analyze_scores, name='analyze_scores'),
]
