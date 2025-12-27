"""
Admin configuration for the todo application.

This module configures the Django admin interface for managing tasks and contact messages.
"""
from django.contrib import admin
from .models import Task, ContactMessage


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Task model.
    
    Provides a user-friendly interface for managing tasks in the admin panel.
    """
    list_display = ('title', 'completed', 'due_date', 'user', 'created_at', 'updated_at')
    list_filter = ('completed', 'due_date', 'created_at', 'user')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('completed',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'user', 'completed', 'due_date')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the ContactMessage model.
    
    Provides interface for viewing and managing contact messages from users.
    """
    list_display = ('name', 'email', 'is_read', 'created_at', 'message_preview')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Информация об отправителе', {
            'fields': ('name', 'email')
        }),
        ('Сообщение', {
            'fields': ('message', 'is_read')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def message_preview(self, obj):
        """Return a preview of the message (first 50 characters)."""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Предпросмотр сообщения'

