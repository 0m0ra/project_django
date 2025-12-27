"""
URL configuration for the todo application.

Defines all URL patterns for task-related views.
"""
from django.urls import path
from . import views

app_name = 'todo_app'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<int:task_id>/toggle/', views.task_toggle, name='task_toggle'),
    path('<int:task_id>/delete/', views.task_delete, name='task_delete'),
    # Calendar view
    path('calendar/', views.calendar_view, name='calendar'),
    # Contact page
    path('contact/', views.contact_view, name='contact'),
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

