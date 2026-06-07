# TaskTide Notifications Guide

Этот документ содержит только специализированные детали по системе уведомлений.
Базовый запуск проекта, структура и установка описаны в `README.md`.

## Что входит в подсистему уведомлений

- `notification_service.py` — фоновый сервис дедлайн-уведомлений (CLI: `start|stop|status|restart`)
- `notification_service_window.py` — вариант уведомлений в виде окон
- `start_notifications.sh` — shell-обёртка для управления сервисом
- `assets/sounds/jink.mp3` — основной звук уведомления

## Быстрое управление сервисом

```bash
python3 notification_service.py start
python3 notification_service.py status
python3 notification_service.py stop
python3 notification_service.py restart
```

Альтернатива через shell:

```bash
./start_notifications.sh start
./start_notifications.sh status
./start_notifications.sh stop
./start_notifications.sh restart
```

## Как это работает

- сервис проверяет дедлайны с периодом `check_interval` (по умолчанию 60 секунд)
- для задач, попавших в окно уведомления, показывает системное уведомление
- при наличии `pygame` воспроизводит звук
- PID/runtime-файлы хранятся в `data/runtime/`

## Зависимости

- обязательно: Python 3
- опционально (рекомендуется):
  - `pygame` — звук
  - `plyer` — системные уведомления

Установка:

```bash
pip install pygame plyer
```

## Конфигурация

Основные точки для настройки находятся в `src/tasktide/notification_service.py`:
- `self.check_interval` — частота проверки
- интервалы и логика показа — в `check_notifications()` и связанных helper-функциях

## Диагностика

### Сервис «не запущен»
- проверь командой `python3 notification_service.py status`
- проверь, что файл запускается тем же Python-окружением

### Нет звука
- проверь `assets/sounds/jink.mp3`
- проверь установку `pygame`

### Нет системных уведомлений
- проверь системные разрешения уведомлений
- проверь установку `plyer`
- смотри вывод сервиса в консоли

## Границы ответственности

- `README.md` — общий гайд по проекту
- `NOTIFICATIONS_README.md` — только углублённые детали уведомлений
