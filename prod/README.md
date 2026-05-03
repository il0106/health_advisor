## Django многостраничный сайт (минимальный)

Страницы:

- `/` — лендинг
- `/auth/register/` — регистрация по email
- `/auth/login/` — вход по email
- `/me/` — защищённая страница (без авторизации редиректит на вход)
- `/monitor/` — монитор FatSecret (только для авторизованных): синхронизация профиля и дневника в Postgres

В `.env` для FatSecret задайте ключи приложения (как в ноутбуке): `ConsumerKey` и `ConsumerSecret`, либо `FATSECRET_CONSUMER_KEY` и `FATSECRET_CONSUMER_SECRET`. Глубина истории дневника: `FATSECRET_FOOD_DIARY_DAYS` (смещение начала периода от даты синхронизации; период включает конечную дату).

Один раз откройте `/monitor/connect/`, пройдите OAuth (ссылка + PIN), затем на `/monitor/` нажмите «Обновить данные».

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

Postgres разворачивается отдельным контейнером `db`, а данные БД сохраняются в docker volume `pgdata`, поэтому **не перезатираются при перезапуске**.

### Запуск без Docker (опционально)

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

