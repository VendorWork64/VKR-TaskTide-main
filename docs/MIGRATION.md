# Migration Notes

## What changed

1. Python-код перенесён из корня в `src/tasktide/`.
2. Добавлен единый модуль путей (`src/tasktide/paths.py`).
3. База данных использует `data/local/tasks.db`.
4. Runtime PID-файлы перенесены в `data/runtime/`.
5. Звуковые файлы перенесены в `assets/sounds/`.
6. Служебные скрипты вынесены в `scripts/`.
7. Устаревшие корневые артефакты перенесены в `archive/legacy_root/`.

## Backward compatibility

- В корне оставлены proxy-файлы с прежними именами модулей.
- Запуск через старые команды сохранён:
  - `python3 backend_api.py`
  - `python3 notification_service.py start|stop|status|restart`
  - `python3 notification_service_window.py start|stop|status|restart`

## Next cleanup (optional)

1. После стабилизации можно удалить часть proxy-файлов и перевести импорты на `src.tasktide.*` напрямую.
2. Добавить тесты smoke-запуска для `main.py`, `server/api_server.py`, `electron`.
