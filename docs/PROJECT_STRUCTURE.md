# Project Structure (Current)

## Root (kept minimal)
- `main.py` — launcher (Electron first, then PyQt fallback)
- `main_qml.py` — QML entrypoint
- compatibility proxy modules (`database.py`, `ui.py`, `backend_api.py`, etc.)
- `electron/` — frontend and builds
- `server/` — standalone API server
- `src/` — main Python source package
- `assets/` — static assets
- `data/` — local and runtime data
- `scripts/` — helper scripts
- `docs/` — docs
- `archive/` — archived legacy files
- `Приложение я хочу поменять иконку.dmg и .exe./` — intentionally kept in root

## Source package
- `src/tasktide/` — active implementation modules
  - UI modules (`ui*.py`)
  - data modules (`database.py`, `notes_db.py`)
  - services (`notification_service*.py`)
  - path management (`paths.py`)

## Data layout
- `data/local/tasks.db` — active SQLite DB
- `data/runtime/` — PID/runtime files
- `assets/sounds/` — active sound files

## Archive
- `archive/legacy_root/` — old root artifacts moved out of active root

## Compatibility policy
Proxy modules remain in root to avoid breaking old imports and old start commands.
