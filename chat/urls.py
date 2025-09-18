from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('create_chat/', views.create_chat, name='create_chat'),
    path('send_message/', views.send_message, name='send_message'),
    path('chat/<int:chat_id>/messages/', views.get_messages, name='get_messages'),
    path('chat/<int:chat_id>/update_title/', views.update_chat_title, name='update_title'),
    path('chat/<int:chat_id>/delete/', views.delete_chat, name='delete_chat'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('top_up_balance/', views.top_up_balance, name='top_up_balance'),
]