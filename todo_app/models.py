"""
Models for the todo application.

This module contains the Task model which represents a single todo item.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """
    Model representing a single task in the todo list.
    
    Attributes:
        title: The text content of the task
        completed: Boolean flag indicating if the task is completed
        created_at: Timestamp when the task was created
        user: Foreign key to the User who owns this task
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название задачи',
        help_text='Введите текст задачи'
    )
    completed = models.BooleanField(
        default=False,
        verbose_name='Выполнено',
        help_text='Отметьте, если задача выполнена'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время создания задачи'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
        help_text='Дата и время последнего обновления'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Срок выполнения',
        help_text='Дата, к которой нужно выполнить задачу'
    )

    class Meta:
        """Meta options for the Task model."""
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the Task."""
        status = "✓" if self.completed else "○"
        return f"{status} {self.title}"


class ContactMessage(models.Model):
    """
    Model representing a contact message from users.
    
    Stores messages sent through the contact form for admin review.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Имя',
        help_text='Имя отправителя'
    )
    email = models.EmailField(
        verbose_name='Email',
        help_text='Email адрес отправителя'
    )
    message = models.TextField(
        verbose_name='Сообщение',
        help_text='Текст сообщения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отправки',
        help_text='Дата и время отправки сообщения'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано',
        help_text='Отметьте, если сообщение прочитано'
    )

    class Meta:
        """Meta options for the ContactMessage model."""
        verbose_name = 'Сообщение обратной связи'
        verbose_name_plural = 'Сообщения обратной связи'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the ContactMessage."""
        read_status = "✓" if self.is_read else "○"
        return f"{read_status} {self.name} - {self.email}"

