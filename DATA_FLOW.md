# Поток данных в приложении To-Do List

## Общий поток данных

Поток данных показывает, как информация движется от пользователя через все компоненты приложения и обратно.

```
ПОЛЬЗОВАТЕЛЬ (Браузер)
    ↓
JavaScript (AJAX/Fetch)
    ↓
HTTP Request (POST/GET)
    ↓
Django URL Router
    ↓
VIEW (обработка запроса)
    ↓
FORM (валидация)
    ↓
MODEL (ORM запросы)
    ↓
БАЗА ДАННЫХ (SQLite)
    ↓
MODEL (возврат данных)
    ↓
VIEW (обработка результата)
    ↓
TEMPLATE (генерация HTML)
    ↓
HTTP Response
    ↓
JavaScript (обновление UI)
    ↓
ПОЛЬЗОВАТЕЛЬ (видит результат)
```

---

## Пример 1: Создание задачи (полный поток)

### Шаг 1: Пользователь вводит данные

**Где:** Браузер (HTML форма)

```html
<!-- task_list.html -->
<form method="post" id="task-form">
    <input type="text" name="title" value="Купить молоко">
    <input type="date" name="due_date" value="2025-12-30">
    <button type="submit">+</button>
</form>
```

**Данные:**
- `title`: "Купить молоко"
- `due_date`: "2025-12-30"

---

### Шаг 2: JavaScript перехватывает отправку

**Где:** `static/js/main.js`

```javascript
function handleTaskCreate(e) {
    e.preventDefault(); // Отменяем стандартную отправку
    
    const form = e.target;
    const formData = new FormData(form);
    // formData содержит: title="Купить молоко", due_date="2025-12-30"
    
    // Добавляем CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // Отправляем AJAX-запрос
    fetch('/create/', {
        method: 'POST',
        body: formData
    })
}
```

**Данные отправляются:** HTTP POST запрос с FormData

---

### Шаг 3: URL Router определяет маршрут

**Где:** `todo_app/urls.py`

```python
urlpatterns = [
    path('create/', views.task_create, name='task_create'),
]
```

**Что происходит:**
- Django получает запрос на `/create/`
- Находит соответствующий URL-паттерн
- Вызывает функцию `views.task_create(request)`

**Данные:** `request` объект с POST данными

---

### Шаг 4: View обрабатывает запрос

**Где:** `todo_app/views.py`

```python
@require_POST
def task_create(request):
    # 1. Получаем данные из запроса
    form = TaskForm(request.POST)
    # request.POST содержит: {'title': 'Купить молоко', 'due_date': '2025-12-30', ...}
    
    # 2. Валидация через форму
    if form.is_valid():
        # 3. Создаем объект задачи (но не сохраняем)
        task = form.save(commit=False)
        # task.title = "Купить молоко"
        # task.due_date = date(2025, 12, 30)
        
        # 4. Добавляем пользователя (если авторизован)
        if request.user.is_authenticated:
            task.user = request.user
        
        # 5. Сохраняем в базу данных
        task.save()
        
        # 6. Возвращаем JSON ответ для AJAX
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'completed': task.completed
            }
        })
```

**Данные обрабатываются:** Валидация, создание объекта Task

---

### Шаг 5: Form валидирует данные

**Где:** `todo_app/forms.py`

```python
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'due_date']
```

**Что происходит:**
- Django автоматически валидирует данные
- Проверяет, что `title` не пустой (max_length=200)
- Проверяет формат `due_date`
- Если ошибки → `form.is_valid()` вернет `False`

**Данные валидируются:** Проверка корректности

---

### Шаг 6: Model сохраняет в базу данных

**Где:** `todo_app/models.py` + Django ORM

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    # ...
```

**Что происходит:**
```python
task.save()  # Вызывается метод save() модели
```

**Django ORM автоматически создает SQL:**
```sql
INSERT INTO todo_app_task 
(title, due_date, completed, created_at, updated_at, user_id) 
VALUES 
('Купить молоко', '2025-12-30', 0, '2025-12-26 23:00:00', '2025-12-26 23:00:00', 1);
```

**Данные сохраняются:** В таблицу `todo_app_task`

---

### Шаг 7: База данных возвращает результат

**Где:** SQLite Database

**Что происходит:**
- SQLite выполняет INSERT запрос
- Создает новую запись с автоматическим ID
- Возвращает подтверждение

**Данные:** Новая запись в базе данных

---

### Шаг 8: View возвращает ответ

**Где:** `todo_app/views.py`

```python
return JsonResponse({
    'success': True,
    'task': {
        'id': 42,  # Автоматически сгенерированный ID
        'title': 'Купить молоко',
        'completed': False
    }
})
```

**Данные возвращаются:** JSON ответ

---

### Шаг 9: JavaScript получает ответ

**Где:** `static/js/main.js`

```javascript
fetch('/create/', {...})
    .then(response => response.json())
    .then(data => {
        // data = {success: true, task: {id: 42, title: 'Купить молоко', ...}}
        if (data.success) {
            // Обновляем страницу, чтобы показать новую задачу
            window.location.reload();
        }
    })
```

**Данные обрабатываются:** Обновление интерфейса

---

### Шаг 10: Страница перезагружается, показывая новую задачу

**Где:** `todo_app/views.py` → `task_list()`

```python
def task_list(request):
    # Получаем задачи из базы данных
    tasks = Task.objects.filter(user=request.user)
    # Теперь tasks содержит новую задачу с id=42
    
    active_tasks = tasks.filter(completed=False)
    # active_tasks теперь включает "Купить молоко"
    
    return render(request, 'todo_app/task_list.html', {
        'active_tasks': active_tasks
    })
```

**Данные передаются в Template:** Контекст с задачами

---

### Шаг 11: Template отображает данные

**Где:** `todo_app/templates/todo_app/task_list.html`

```django
{% for task in active_tasks %}
    <li class="task-item">
        <span>{{ task.title }}</span>
        {% if task.due_date %}
            <span>📅 {{ task.due_date|date:"d.m.Y" }}</span>
        {% endif %}
    </li>
{% endfor %}
```

**Результат в HTML:**
```html
<li class="task-item">
    <span>Купить молоко</span>
    <span>📅 30.12.2025</span>
</li>
```

**Данные отображаются:** HTML страница с новой задачей

---

### Шаг 12: Пользователь видит результат

**Где:** Браузер

Пользователь видит новую задачу "Купить молоко" в списке активных задач с датой 30.12.2025.

---

## Пример 2: Отметка задачи как выполненной (AJAX без перезагрузки)

### Поток данных:

```
1. ПОЛЬЗОВАТЕЛЬ
   Кликает на чекбокс задачи
   ↓
2. JavaScript (main.js)
   Перехватывает событие change
   Сразу меняет вид задачи (оптимистично)
   ↓
3. AJAX запрос
   POST /42/toggle/
   ↓
4. URL Router
   Вызывает views.task_toggle(request, task_id=42)
   ↓
5. VIEW (views.py)
   Получает задачу: task = Task.objects.get(id=42)
   Меняет статус: task.completed = True
   Сохраняет: task.save()
   ↓
6. MODEL → БД
   UPDATE todo_app_task SET completed=1 WHERE id=42
   ↓
7. VIEW возвращает JSON
   {'success': True, 'completed': True}
   ↓
8. JavaScript получает ответ
   Перемещает задачу в секцию "Выполненные"
   Обновляет статистику
   ↓
9. ПОЛЬЗОВАТЕЛЬ
   Видит задачу в секции "Выполненные" (без перезагрузки)
```

---

## Пример 3: Просмотр календаря

### Поток данных:

```
1. ПОЛЬЗОВАТЕЛЬ
   Открывает /calendar/?year=2025&month=12
   ↓
2. URL Router
   Вызывает views.calendar_view(request)
   ↓
3. VIEW (views.py)
   Получает параметры: year=2025, month=12
   Вычисляет диапазон дат: first_day, last_day
   ↓
4. MODEL (ORM запрос)
   tasks = Task.objects.filter(
       due_date__gte=first_day,
       due_date__lte=last_day
   )
   ↓
5. БАЗА ДАННЫХ
   SELECT * FROM todo_app_task 
   WHERE due_date >= '2025-12-01' 
   AND due_date <= '2025-12-31'
   ↓
6. MODEL возвращает QuerySet
   [<Task: Купить молоко>, <Task: Позвонить маме>, ...]
   ↓
7. VIEW обрабатывает данные
   Группирует задачи по датам:
   {
       '2025-12-30': [<Task: Купить молоко>],
       '2025-12-25': [<Task: Позвонить маме>]
   }
   Создает список дней календаря
   ↓
8. VIEW передает в Template
   context = {
       'calendar_days': [...],
       'year': 2025,
       'month': 12
   }
   ↓
9. TEMPLATE (calendar.html)
   Отображает календарную сетку
   Вставляет задачи в соответствующие дни
   ↓
10. ПОЛЬЗОВАТЕЛЬ
    Видит календарь с задачами
```

---

## Типы потоков данных в нашем приложении

### 1. **Создание данных (CREATE)**

**Поток:**
```
Форма → JavaScript → AJAX → View → Form → Model → БД → JSON → JavaScript → Перезагрузка
```

**Примеры:**
- Создание задачи
- Отправка сообщения обратной связи
- Регистрация пользователя

---

### 2. **Чтение данных (READ)**

**Поток:**
```
URL → View → Model → БД → QuerySet → View → Template → HTML
```

**Примеры:**
- Просмотр списка задач
- Просмотр календаря
- Просмотр страницы контактов

---

### 3. **Обновление данных (UPDATE)**

**Поток:**
```
Событие → JavaScript → AJAX → View → Model → БД → JSON → JavaScript → UI
```

**Примеры:**
- Отметка задачи как выполненной
- Переключение статуса задачи

---

### 4. **Удаление данных (DELETE)**

**Поток:**
```
Клик → Подтверждение → JavaScript → AJAX → View → Model → БД → JSON → JavaScript → Анимация → Удаление из DOM
```

**Примеры:**
- Удаление задачи

---

## Детальный разбор: создание задачи

### Данные на каждом этапе:

**1. HTML форма:**
```html
<input name="title" value="Купить молоко">
<input name="due_date" value="2025-12-30">
```

**2. JavaScript FormData:**
```javascript
FormData {
    title: "Купить молоко",
    due_date: "2025-12-30",
    csrfmiddlewaretoken: "abc123..."
}
```

**3. HTTP Request:**
```
POST /create/ HTTP/1.1
Content-Type: multipart/form-data

title=Купить+молоко&due_date=2025-12-30&csrfmiddlewaretoken=abc123...
```

**4. Django request.POST:**
```python
<QueryDict: {
    'title': ['Купить молоко'],
    'due_date': ['2025-12-30'],
    'csrfmiddlewaretoken': ['abc123...']
}>
```

**5. Form объект:**
```python
TaskForm({
    'title': 'Купить молоко',
    'due_date': '2025-12-30'
})
# form.is_valid() = True
```

**6. Model объект (до сохранения):**
```python
Task(
    title='Купить молоко',
    due_date=date(2025, 12, 30),
    completed=False,
    user=None  # или User объект
)
# id еще не присвоен
```

**7. SQL запрос:**
```sql
INSERT INTO todo_app_task 
(title, due_date, completed, created_at, updated_at, user_id) 
VALUES 
('Купить молоко', '2025-12-30', 0, '2025-12-26 23:00:00', '2025-12-26 23:00:00', 1);
```

**8. База данных:**
```
id | title          | due_date   | completed | created_at          | user_id
42 | Купить молоко  | 2025-12-30 | 0         | 2025-12-26 23:00:00 | 1
```

**9. JSON ответ:**
```json
{
    "success": true,
    "task": {
        "id": 42,
        "title": "Купить молоко",
        "completed": false
    }
}
```

**10. Обновленная страница:**
```html
<li class="task-item" data-task-id="42">
    <span>Купить молоко</span>
    <span>📅 30.12.2025</span>
</li>
```

---

## Особенности потока данных в нашем приложении

### 1. **AJAX для интерактивности**

**Без AJAX:**
```
Действие → Полная перезагрузка страницы → Новый HTML
```

**С AJAX:**
```
Действие → AJAX запрос → JSON ответ → Обновление только нужной части
```

**Преимущества:**
- Быстрее (нет перезагрузки)
- Сохраняется состояние страницы
- Плавные анимации

---

### 2. **Оптимистичное обновление UI**

**Поток:**
```
1. Пользователь кликает
2. JavaScript сразу меняет UI (оптимистично)
3. Отправляет запрос на сервер
4. Если успех → изменения остаются
5. Если ошибка → откатывает изменения
```

**Пример:**
```javascript
// Сразу меняем вид
taskItem.classList.add('completed');

// Отправляем запрос
fetch('/toggle/', {...})
    .then(data => {
        if (!data.success) {
            // Откатываем, если ошибка
            taskItem.classList.remove('completed');
        }
    });
```

---

### 3. **Валидация на нескольких уровнях**

**Поток валидации:**
```
1. HTML5 валидация (required, type="email")
2. JavaScript валидация (проверка пустых полей)
3. Django Form валидация (на сервере)
4. Model валидация (ограничения БД)
```

**Пример:**
```python
# 1. HTML: <input required>
# 2. JavaScript: if (!inputValue) return;
# 3. Form: form.is_valid()  # проверяет max_length, формат
# 4. Model: CharField(max_length=200)  # ограничение в БД
```

---

### 4. **Контекст для Template**

**Как данные передаются в Template:**

```python
# View создает контекст
context = {
    'active_tasks': QuerySet([<Task>, <Task>, ...]),
    'completed_tasks': QuerySet([<Task>]),
    'total_tasks': 5,
    'today': date(2025, 12, 26)
}

# Передается в Template
return render(request, 'task_list.html', context)

# Template использует данные
{% for task in active_tasks %}
    {{ task.title }}  # Доступ к полям модели
{% endfor %}
```

---

## Схема полного потока данных

```
┌─────────────────────────────────────────────────────────────┐
│                    ПОЛЬЗОВАТЕЛЬ                             │
│              (Ввод данных, клики, просмотр)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  БРАУЗЕР (HTML/CSS/JS)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   HTML       │  │  JavaScript  │  │   AJAX       │     │
│  │  Формы       │  │  Обработчики │  │  Fetch API   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP Request (POST/GET)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              DJANGO URL ROUTER                                │
│              (urls.py)                                       │
│  Определяет: какой View вызвать для данного URL              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    VIEW                                      │
│                  (views.py)                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  1. Получает request с данными                       │  │
│  │  2. Создает/использует Form для валидации            │  │
│  │  3. Обращается к Model для работы с данными          │  │
│  │  4. Обрабатывает бизнес-логику                        │  │
│  │  5. Создает контекст для Template                     │  │
│  │  6. Возвращает ответ (render/redirect/JsonResponse)  │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────┬───────────────────────────┬─────────────────────┘
            │                           │
            ↓                           ↓
┌──────────────────────┐    ┌──────────────────────────┐
│      FORM            │    │        MODEL              │
│    (forms.py)        │    │      (models.py)          │
│                      │    │                           │
│ - Валидация данных   │    │ - Определяет структуру    │
│ - Преобразование     │    │ - ORM запросы             │
│ - Очистка данных     │    │ - Бизнес-логика           │
└──────────────────────┘    └───────────┬──────────────┘
                                         │
                                         ↓
                        ┌──────────────────────────────┐
                        │      БАЗА ДАННЫХ             │
                        │      (SQLite)                │
                        │                              │
                        │ - Хранение данных            │
                        │ - Выполнение SQL-запросов     │
                        │ - Возврат результатов        │
                        └───────────┬──────────────────┘
                                    │
                                    │ QuerySet / Объекты
                                    ↓
                        ┌──────────────────────────────┐
                        │        MODEL                 │
                        │   Возвращает данные          │
                        └───────────┬──────────────────┘
                                    │
                                    ↓
                        ┌──────────────────────────────┐
                        │        VIEW                  │
                        │   Обрабатывает результат     │
                        │   Создает контекст           │
                        └───────────┬──────────────────┘
                                    │
                                    │ context = {...}
                                    ↓
                        ┌──────────────────────────────┐
                        │      TEMPLATE                │
                        │   (templates/*.html)          │
                        │                              │
                        │ - Получает контекст          │
                        │ - Генерирует HTML           │
                        │ - Форматирует данные         │
                        └───────────┬──────────────────┘
                                    │
                                    │ HTML
                                    ↓
                        ┌──────────────────────────────┐
                        │   HTTP RESPONSE              │
                        │   (HTML/JSON)                │
                        └───────────┬──────────────────┘
                                    │
                                    ↓
                        ┌──────────────────────────────┐
                        │      БРАУЗЕР                 │
                        │   - Отображает HTML          │
                        │   - Выполняет JavaScript      │
                        │   - Обновляет UI             │
                        └───────────┬──────────────────┘
                                    │
                                    ↓
                        ┌──────────────────────────────┐
                        │      ПОЛЬЗОВАТЕЛЬ            │
                        │   Видит результат             │
                        └──────────────────────────────┘
```

---

## Итог

### Поток данных в нашем приложении:

1. **Входные данные:** Пользователь вводит данные в форму или выполняет действие
2. **JavaScript:** Перехватывает события, отправляет AJAX-запросы
3. **URL Router:** Определяет, какой View обработает запрос
4. **View:** Получает данные, валидирует через Form, обращается к Model
5. **Model:** Взаимодействует с базой данных через ORM
6. **База данных:** Хранит и возвращает данные
7. **View:** Обрабатывает результат, создает контекст
8. **Template:** Генерирует HTML из контекста
9. **JavaScript:** Обновляет интерфейс (AJAX) или перезагружает страницу
10. **Пользователь:** Видит результат своих действий

**Ключевые особенности:**
- ✅ AJAX для быстрых обновлений
- ✅ Оптимистичное обновление UI
- ✅ Многоуровневая валидация
- ✅ Четкое разделение ответственности (MTV)

