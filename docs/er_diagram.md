# ER-диаграмма базы данных

## Описание структуры

```
┌─────────────────┐
│      User       │
│  (Django Auth)  │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ password        │
│ ...             │
└────────┬────────┘
         │
         │ 1:N
         │
         │
┌────────▼────────┐
│      Task       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ completed       │
│ created_at      │
│ updated_at      │
│ user_id (FK)    │──┐
└─────────────────┘  │
                     │
                     │ (опциональная связь)
                     │
                     └─── User может иметь много Task
```

## Связи

- **User** (1) ──< (N) **Task**: Один пользователь может иметь множество задач
- Связь опциональная: задачи могут существовать без пользователя (для демо-режима)

## Поля модели Task

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | AutoField | Primary Key | Автоматически генерируемый ID |
| `title` | CharField | max_length=200, NOT NULL | Текст задачи |
| `completed` | BooleanField | default=False | Статус выполнения |
| `created_at` | DateTimeField | auto_now_add=True | Дата создания |
| `updated_at` | DateTimeField | auto_now=True | Дата обновления |
| `user` | ForeignKey | on_delete=CASCADE, null=True | Связь с пользователем |

## Индексы

- Автоматический индекс на `user_id` (ForeignKey)
- Сортировка по умолчанию: `-created_at` (новые задачи первыми)

