## Django многостраничный сайт (минимальный)

Страницы:

- `/` — лендинг
- `/auth/register/` — регистрация по email
- `/auth/login/` — вход по email
- `/me/` — защищённая страница (без авторизации редиректит на вход)

### Запуск в Docker

Из папки `prod`:

```bash
docker compose up --build
```

Открыть: `http://localhost:8000`

Админка: `http://localhost:8000/admin/`

Суперпользователь создаётся автоматически при старте контейнера из `.env`:

- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

База данных пользователей сохраняется в docker volume (см. `DJANGO_DB_PATH=/data/db.sqlite3`), поэтому **не перезатирается при перезапуске контейнера**.

### Запуск без Docker (опционально)

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

