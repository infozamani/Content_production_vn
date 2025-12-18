from django.urls import path
from apps.dashboard import views

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    path('generate/<int:project_id>/', views.start_generation, name='start_generation'),
    path('upload/<int:project_id>/', views.upload_youtube, name='upload_youtube'),
    
    # مسیرهای جدید
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('upload-telegram/<int:project_id>/', views.upload_telegram, name='upload_telegram'),

]