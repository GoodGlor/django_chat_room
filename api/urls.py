from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes, name='api'),
    path('rooms/', views.get_rooms, name='rooms_api'),
    path('room/<str:pk>', views.get_room, name='room_api'),

]
