# Документация проекта To-Do List

Эта папка содержит дополнительную документацию проекта.

## Файлы

- `er_diagram.md` - ER-диаграмма базы данных в текстовом формате
- `architecture.md` - Архитектурная схема приложения
- `README.md` - Этот файл

## Создание визуальных диаграмм

Для создания визуальных версий диаграмм можно использовать:

1. **draw.io** (https://app.diagrams.net/)
   - Импортируйте структуру из `er_diagram.md`
   - Экспортируйте в PNG/SVG

2. **dbdiagram.io** (https://dbdiagram.io/)
   - Используйте для создания ER-диаграмм
   - Код для dbdiagram:
   ```sql
   Table User {
     id integer [primary key]
     username varchar
     email varchar
   }
   
   Table Task {
     id integer [primary key]
     title varchar
     completed boolean
     created_at datetime
     updated_at datetime
     user_id integer [ref: > User.id]
   }
   ```

3. **Mermaid** (для Markdown)
   - Можно использовать в README.md
   - Пример:
   ```mermaid
   erDiagram
       User ||--o{ Task : has
       User {
           int id
           string username
       }
       Task {
           int id
           string title
           boolean completed
       }
   ```

## Скриншоты

Папка `screenshots/` должна содержать скриншоты приложения:
- `main_page.png` - Главная страница
- `add_task.png` - Добавление задачи
- `admin_panel.png` - Админ-панель
- `stats.png` - Статистика
- `mobile.png` - Мобильная версия

