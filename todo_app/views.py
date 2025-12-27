"""
Views for the todo application.

This module contains all view functions for handling HTTP requests
related to task management (CRUD operations) and user authentication.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
from calendar import monthrange
from .models import Task, ContactMessage
from .forms import TaskForm, CustomUserCreationForm, CustomAuthenticationForm, ContactForm


def task_list(request):
    """
    Display a list of all tasks.
    
    Shows active tasks first, then completed tasks at the bottom.
    If user is authenticated, shows only their tasks.
    Otherwise, shows all tasks (for demo purposes).
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered template with task list
    """
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user)
    else:
        tasks = Task.objects.filter(user__isnull=True)
    
    # Separate active and completed tasks
    active_tasks = tasks.filter(completed=False)
    completed_tasks = tasks.filter(completed=True)
    
    context = {
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
        'total_tasks': tasks.count(),
        'completed_count': completed_tasks.count(),
        'today': timezone.now().date(),
    }
    
    return render(request, 'todo_app/task_list.html', context)


@require_POST
def task_create(request):
    """
    Create a new task.
    
    Handles POST requests to create a new task. If user is authenticated,
    assigns the task to that user.
    
    Args:
        request: HTTP request object with POST data
        
    Returns:
        Redirect to task list or JSON response for AJAX requests
    """
    form = TaskForm(request.POST)
    
    if form.is_valid():
        task = form.save(commit=False)
        if request.user.is_authenticated:
            task.user = request.user
        task.save()
        messages.success(request, 'Задача успешно добавлена!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'completed': task.completed,
                }
            })
    else:
        messages.error(request, 'Ошибка при добавлении задачи.')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return redirect('todo_app:task_list')


@require_POST
def task_toggle(request, task_id):
    """
    Toggle the completion status of a task.
    
    Switches the task between completed and not completed states.
    
    Args:
        request: HTTP request object
        task_id: ID of the task to toggle
        
    Returns:
        JSON response with updated task status
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user owns the task or task has no owner
    if request.user.is_authenticated:
        if task.user and task.user != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
    else:
        if task.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    task.completed = not task.completed
    task.save()
    
    return JsonResponse({
        'success': True,
        'completed': task.completed,
        'task_id': task.id
    })


@require_POST
def task_delete(request, task_id):
    """
    Delete a task.
    
    Permanently removes a task from the database.
    
    Args:
        request: HTTP request object
        task_id: ID of the task to delete
        
    Returns:
        JSON response or redirect
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user owns the task or task has no owner
    if request.user.is_authenticated:
        if task.user and task.user != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
    else:
        if task.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    task.delete()
    messages.success(request, 'Задача удалена!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('todo_app:task_list')


def register_view(request):
    """
    Handle user registration.
    
    Displays registration form and processes new user signups.
    After successful registration, logs the user in and redirects to task list.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered registration template or redirect to task list
    """
    if request.user.is_authenticated:
        return redirect('todo_app:task_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
            return redirect('todo_app:task_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'todo_app/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    
    Displays login form and authenticates users.
    After successful login, redirects to task list.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered login template or redirect to task list
    """
    if request.user.is_authenticated:
        return redirect('todo_app:task_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'todo_app:task_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'todo_app/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Handle user logout.
    
    Logs out the current user and redirects to task list.
    
    Args:
        request: HTTP request object
        
    Returns:
        Redirect to task list
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Вы успешно вышли из аккаунта.')
    return redirect('todo_app:task_list')


def calendar_view(request):
    """
    Display tasks in a calendar view.
    
    Shows a monthly calendar with tasks grouped by their due dates.
    If user is authenticated, shows only their tasks.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered template with calendar view
    """
    # Get year and month from request, default to current
    today = timezone.now().date()
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    
    try:
        year = int(year)
        month = int(month)
        # Validate month
        if month < 1 or month > 12:
            month = today.month
            year = today.year
    except (ValueError, TypeError):
        year = today.year
        month = today.month
    
    # Get first day of month
    first_day = datetime(year, month, 1).date()
    # Get number of days in month
    days_in_month = monthrange(year, month)[1]
    # Get last day of month
    last_day = datetime(year, month, days_in_month).date()
    
    # Get tasks for the month
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user, due_date__gte=first_day, due_date__lte=last_day)
    else:
        tasks = Task.objects.filter(user__isnull=True, due_date__gte=first_day, due_date__lte=last_day)
    
    # Group tasks by date
    tasks_by_date = {}
    for task in tasks:
        if task.due_date:
            date_key = task.due_date.isoformat()
            if date_key not in tasks_by_date:
                tasks_by_date[date_key] = []
            tasks_by_date[date_key].append(task)
    
    # Calculate previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Get weekday of first day (0 = Monday, 6 = Sunday)
    first_weekday = first_day.weekday()
    
    # Create list of days for the calendar
    calendar_days = []
    # Add empty days for the first week
    for i in range(first_weekday):
        calendar_days.append({'day': None, 'date': None, 'tasks': []})
    
    # Add days of the month
    for day in range(1, days_in_month + 1):
        current_date = datetime(year, month, day).date()
        date_key = current_date.isoformat()
        day_tasks = tasks_by_date.get(date_key, [])
        calendar_days.append({
            'day': day,
            'date': current_date,
            'date_key': date_key,
            'tasks': day_tasks,
            'is_today': current_date == today,
            'is_past': current_date < today,
        })
    
    context = {
        'year': year,
        'month': month,
        'month_name': first_day.strftime('%B'),
        'month_name_ru': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                         'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month - 1],
        'first_day': first_day,
        'last_day': last_day,
        'days_in_month': days_in_month,
        'first_weekday': first_weekday,
        'calendar_days': calendar_days,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today,
    }
    
    return render(request, 'todo_app/calendar.html', context)


def contact_view(request):
    """
    Display contact page and handle contact form submissions.
    
    Shows contact information and a form for users to send messages.
    Messages are saved to the database and visible in admin panel.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered template with contact form or redirect after submission
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.')
            return redirect('todo_app:contact')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ContactForm()
    
    # Contact information
    contact_info = {
        'name': 'Старцев Захар Вадимович',
        'phone': '89132081749',
        'email': 'onamo21@mail.ru',
    }
    
    context = {
        'form': form,
        'contact_info': contact_info,
    }
    
    return render(request, 'todo_app/contact.html', context)

