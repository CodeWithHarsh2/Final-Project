from django.urls import path
from . import views

urlpatterns = [
    path('', views.quest_list, name='quest_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('complete_challenge/', views.complete_challenge, name='complete_challenge'),
    path('create/', views.create_quest, name='create_quest'),
    path('add-badge/', views.create_badge, name='create_badge'),
    path('delete-quest/<int:quest_id>/', views.delete_quest, name='delete_quest'),

]

