from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_chat/', views.create_chat, name='create_chat'),
    path('send_message/', views.send_message, name='send_message'),
    path('chat/<int:chat_id>/messages/', views.get_messages, name='get_messages'),
    path('chat/<int:chat_id>/update_title/', views.update_chat_title, name='update_title'),
]