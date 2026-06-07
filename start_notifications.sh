#!/bin/bash
# Скрипт для автоматического запуска сервиса уведомлений TaskTide

# Путь к проекту
PROJECT_DIR="/Users/vendor/Desktop/Программирование/Новейший Task"
SERVICE_SCRIPT="$PROJECT_DIR/notification_service.py"

# Функция для запуска сервиса
start_service() {
    echo "🚀 Запускаем сервис уведомлений TaskTide..."
    cd "$PROJECT_DIR"
    python3 "$SERVICE_SCRIPT" start &
    echo "✅ Сервис запущен в фоновом режиме"
}

# Функция для остановки сервиса
stop_service() {
    echo "🛑 Останавливаем сервис уведомлений TaskTide..."
    cd "$PROJECT_DIR"
    python3 "$SERVICE_SCRIPT" stop
    echo "✅ Сервис остановлен"
}

# Функция для проверки статуса
status_service() {
    echo "📊 Проверяем статус сервиса..."
    cd "$PROJECT_DIR"
    python3 "$SERVICE_SCRIPT" status
}

# Функция для перезапуска
restart_service() {
    echo "🔄 Перезапускаем сервис..."
    stop_service
    sleep 2
    start_service
}

# Основная логика
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    status)
        status_service
        ;;
    restart)
        restart_service
        ;;
    *)
        echo "Использование: $0 {start|stop|status|restart}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить сервис уведомлений"
        echo "  stop    - Остановить сервис уведомлений"
        echo "  status  - Показать статус сервиса"
        echo "  restart - Перезапустить сервис"
        exit 1
        ;;
esac

exit 0
