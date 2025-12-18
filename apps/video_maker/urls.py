from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='video_maker_index'),
    path('api/generate-script/', views.generate_script, name='generate_script'),
    path('api/generate-audio/', views.generate_audio, name='generate_audio'),
    path('api/generate-image/', views.generate_image, name='generate_image'),
    path('api/create-project/', views.create_video_project, name='create_project'),
    path('api/project-status/<str:project_id>/', views.project_status, name='project_status'),
    path('test/', views.test_view, name='test_view'),
    path('debug/', views.debug_view, name='debug_view'),  # اضافه کردن صفحه دیباگ
]