from django.urls import path
from downloader import views

urlpatterns = [
    path('health', views.health),
    path('api/download-video/', views.download_video),
    path('api/download-audio/', views.download_audio),
]
