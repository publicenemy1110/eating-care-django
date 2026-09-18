# Eating Care Platform (Django)

Отдельный проект для PyCharm. Статическая HTML/CSS-версия лежит в подпапке `html-css-site/`.

## PyCharm

1. **File → Open** → папка `eating-care-django`
2. **Settings → Project → Python Interpreter** → `eating-care-django/.venv/bin/python`
3. **Run → Edit Configurations → Django Server**:
   - Script: `manage.py`
   - Parameters: `runserver`
   - Working directory: корень проекта

## Первый запуск

```bash
cd eating-care-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

http://127.0.0.1:8000/

## Страницы

| URL | Страница |
|-----|----------|
| `/` | Главная |
| `/rpp/` | Про РПП |
| `/tests/` | Тесты |
| `/parents/` | Для родителей |
| `/programs/` | Программы питания |
| `/about/` | О нас |

## Картинки

Положите файлы в `pages/static/images/` (logo.png, hero-photo.png и т.д.).

## Обновить шаблоны из HTML

После правок в `html-css-site/`:

```bash
python convert_html.py
```
