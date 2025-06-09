from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.quest_list, name='quest_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('complete_challenge/', views.complete_challenge, name='complete_challenge'),
    path('create/', views.create_quest, name='create_quest'),
    path('add-badge/', views.create_badge, name='create_badge'),
    path('delete-quest/<int:quest_id>/', views.delete_quest, name='delete_quest'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('complete_challenge/<int:challenge_id>/', views.complete_challenge, name='complete_challenge'),
    path('register/', views.register, name='register'),
    

]

