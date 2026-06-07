# TaskTide Server

Отдельная серверная часть для TaskTide с:
- регистрацией и авторизацией (`/auth/register`, `/auth/login`, `/auth/me`)
- JWT-доступом к API
- серверной БД SQLite (`server/data/tasktide_server.db`)

## Запуск

```bash
python3 server/api_server.py
```

Опциональные переменные:
- `TASKTIDE_HOST` (по умолчанию `0.0.0.0`)
- `TASKTIDE_PORT` (по умолчанию `8765`)
- `TASKTIDE_DB_PATH` (по умолчанию `server/data/tasktide_server.db`)
- `TASKTIDE_JWT_SECRET` (обязательно сменить в production)
- `TASKTIDE_JWT_TTL_SECONDS` (TTL токена)

## Важно

Electron-клиент должен указывать URL сервера через переменную окружения:

```bash
TASKTIDE_API_BASE=http://<server-host>:8765 npm start
```
