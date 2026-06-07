# TaskTide

TaskTide — desktop-приложение для управления задачами, заметками и фокус-сессиями (Pomodoro).

Проект поддерживает:
- Electron-клиент (основной UI)
- отдельный Python API-сервер (`server/api_server.py`) с JWT-авторизацией
- fallback-режим на PyQt5 через `main.py --pyqt`

## Содержание
- Overview
- Requirements
- Installation
- Quick Start
- Run Modes
- Notifications
- Environment Variables
- Project Structure
- Build and Distribution
- Troubleshooting
- Migration Notes

## Обзор

Текущая целевая архитектура:
1. Electron frontend (`electron/`) общается с API по `TASKTIDE_API_BASE`.
2. API-сервер (`server/api_server.py`) хранит серверные данные в SQLite (`server/data/tasktide_server.db`).
3. Локальная desktop-логика и fallback UI находятся в пакете `src/tasktide/`.

`main.py` умеет автоматически:
- стартовать Electron,
- поднять локальный API (`server/api_server.py`), если он не запущен,
- переключиться на PyQt fallback при ошибке Electron.

## Требования

### Python
- Python 3.10+

### Node.js
- Node.js 18+
- npm 9+

### Python dependencies (minimum)
- для fallback UI: `PyQt5`
- опционально для уведомлений: `pygame`, `plyer`
- для QML-режима: `PySide6`

## Установка

### 1) Clone and enter project

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2) Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install PyQt5 PySide6 pygame plyer
```

Если нужен только основной Electron + API сценарий, `PySide6` не обязателен.

### 3) Install Electron dependencies

```bash
cd electron
npm install
cd ..
```

## Быстрый старт

### Recommended flow (Electron + API)

В одном терминале:
```bash
python3 server/api_server.py
```

Во втором терминале:
```bash
cd electron
TASKTIDE_API_BASE=http://127.0.0.1:8765 npm start
```

## Режимы запуска

### 1) Auto mode (recommended local launcher)

```bash
python3 main.py
```

Что делает:
- инициализирует локальную БД для desktop-части,
- пытается запустить Electron,
- если `TASKTIDE_API_BASE` локальный и API не отвечает — поднимает `server/api_server.py`,
- при неудаче Electron переключается на PyQt fallback.

### 2) Force PyQt fallback

```bash
python3 main.py --pyqt
```

### 3) QML UI (experimental/alt)

```bash
python3 main_qml.py
```

### 4) Legacy root launchers (compatibility)

Сохранены корневые entrypoint-файлы:
- `backend_api.py`
- `notification_service.py`
- `notification_service_window.py`

Они запускают соответствующие модули из `src/tasktide`.

## Уведомления

Кратко:
- дедлайн-уведомления поддерживаются через `notification_service.py`
- звук берётся из `assets/sounds/jink.mp3`
- управление: `start|stop|status|restart`

Подробный специализированный гайд:
- `NOTIFICATIONS_README.md`

## Переменные окружения

### Client / launcher

- `TASKTIDE_API_BASE`
  - URL API для Electron и launcher-проверок
  - default: `http://127.0.0.1:8765`
  - example: `TASKTIDE_API_BASE=http://192.168.1.10:8765`

- `PYTHON_BIN`
  - интерпретатор Python для Electron-сценариев
  - обычно выставляется автоматически launcher’ом

### Server (`server/api_server.py`)

- `TASKTIDE_HOST`
  - default: `0.0.0.0`
- `TASKTIDE_PORT`
  - default: `8765`
- `TASKTIDE_DB_PATH`
  - default: `server/data/tasktide_server.db`
- `TASKTIDE_JWT_SECRET`
  - в production обязателен безопасный секрет
- `TASKTIDE_JWT_SECRET_FILE`
  - default: `server/data/jwt_secret.txt`
- `TASKTIDE_JWT_TTL_SECONDS`
  - TTL access token (seconds)

## Структура проекта

```text
.
├── main.py
├── main_qml.py
├── backend_api.py
├── notification_service.py
├── notification_service_window.py
├── src/
│   └── tasktide/
│       ├── ui_modules/            # UI modules (ui.py, ui2.py, ...)
│       ├── database.py
│       ├── notes_db.py
│       ├── paths.py
│       ├── notification_service.py
│       └── ...
├── server/
│   ├── api_server.py
│   └── data/
├── electron/
├── assets/
│   └── sounds/
├── data/
│   ├── local/
│   └── runtime/
├── docs/
├── scripts/
├── archive/
└── Приложение я хочу поменять иконку.dmg и .exe./
```

Notes:
- `src/tasktide/paths.py` централизует пути к БД/ассетам/runtime-файлам.
- активная локальная БД desktop-части: `data/local/tasks.db`.
- звуки: `assets/sounds/`.

## Сборка и дистрибуция

В `electron/package.json` уже настроен `electron-builder`.

```bash
cd electron
npm install

# unpacked test build
npm run pack

# full build for current OS
npm run dist

# target builds
npm run dist:mac
npm run dist:win
```

Артефакты: `electron/dist`.

## Устранение неполадок

### Electron не запускается
- Проверь `node -v`, `npm -v`.
- Проверь, что `electron/node_modules` установлены (`npm install`).

### Порт API занят
- Ошибка bind на `8765` означает, что порт уже используется.
- Смени порт через `TASKTIDE_PORT` и передай такой же в `TASKTIDE_API_BASE`.

### PyQt fallback не запускается
- Установи `PyQt5`: `pip install PyQt5`.

### Нет звука уведомлений
- Установи `pygame`.
- Проверь наличие файлов в `assets/sounds/`.

### Проблемы с JWT/авторизацией
- Убедись, что задан корректный `TASKTIDE_JWT_SECRET` в production.
- Для локалки можно удалить `server/data/jwt_secret.txt`, чтобы сгенерировать заново.

## Примечания по миграции

Актуальные заметки по реорганизации и миграции:
- `docs/MIGRATION.md`
- `docs/PROJECT_STRUCTURE.md`
