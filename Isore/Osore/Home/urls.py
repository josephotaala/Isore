from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('leader/', views.leader_page, name='leader'),
    path('leader/announce/', views.create_announcement, name='create_announcement'),
    path('member/', views.member_page, name='member'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/upload/', views.upload_photo, name='upload_photo'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]