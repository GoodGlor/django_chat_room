from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_page, name='logout_page'),
    path('', views.home, name='home'),

    path('room/<int:pk>/', views.room, name='room'),
    path('create_room/', views.create_room, name='create_room'),
    path('update_room/<int:pk>/', views.update_room, name='update_room'),
    path('delete_room/<int:pk>/', views.delete_room, name='delete_room'),

    path('delete_message/<int:pk>/', views.delete_message, name='delete_message'),
    path('update_message/<int:pk>/', views.update_message, name='update_message'),

    path('profile/<int:pk>/', views.profile_page, name='profile_page'),
    path('profile_edit/', views.edit_user_page, name='edit_user_page'),

]
