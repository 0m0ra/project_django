"""
Forms for the todo application.

This module contains form classes for task creation and editing,
as well as user registration and authentication.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Task, ContactMessage


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.
    
    Provides text input for task title and date picker for due date.
    """
    class Meta:
        model = Task
        fields = ['title', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите новую задачу...',
                'autofocus': True,
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Выберите дату (необязательно)',
            })
        }
        labels = {
            'title': '',
            'due_date': 'Срок выполнения',
        }


class CustomUserCreationForm(UserCreationForm):
    """
    Custom registration form with improved styling.
    
    Extends Django's UserCreationForm with custom widgets and labels.
    """
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите имя пользователя',
            'autofocus': True,
        }),
        help_text='Обязательное поле. 150 символов или меньше. Только буквы, цифры и @/./+/-/_'
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль',
        }),
        help_text='Пароль должен содержать минимум 8 символов'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтвердите пароль',
        }),
        help_text='Введите тот же пароль для подтверждения'
    )
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите email (необязательно)',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with improved styling.
    
    Extends Django's AuthenticationForm with custom widgets.
    """
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите имя пользователя',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль',
        })
    )


class ContactForm(forms.ModelForm):
    """
    Form for contact messages.
    
    Allows users to send messages through the contact form.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите ваше имя',
                'autofocus': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите ваш email',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Введите ваше сообщение...',
                'rows': 6,
            }),
        }
        labels = {
            'name': 'Ваше имя',
            'email': 'Email',
            'message': 'Сообщение',
        }

