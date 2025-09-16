from django.urls import path
from . import views

app_name = 'video_generator'

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_video, name='generate_video'),
    path('status/<str:task_id>/', views.task_status, name='task_status'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
    path('examples/', views.examples, name='examples'),
]
