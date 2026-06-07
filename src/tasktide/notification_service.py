#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервис фоновых уведомлений для TaskTide
Работает независимо от основного приложения
"""

import time
import os
import sys
import signal
from datetime import datetime, timedelta
from pathlib import Path
from src.tasktide.paths import get_runtime_file, get_sound_path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Импорты для работы с базой данных и уведомлениями
try:
    from src.tasktide.database import get_tasks_approaching_deadline
except ImportError:
    print("Ошибка: Не удалось импортировать модуль database")
    sys.exit(1)

# Импорт для воспроизведения звука
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

# Импорт для системных уведомлений
try:
    from plyer import notification
    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False

class NotificationService:
    """Сервис фоновых уведомлений"""
    
    def __init__(self):
        self.running = True
        self.check_interval = 60  # Проверка каждую минуту
        self.shown_notifications = set()
        self.pid_file = get_runtime_file("notification_service.pid")
        
        # Обработчик сигналов для корректного завершения
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Создаем PID файл
        self.create_pid_file()
        
        print(f"🚀 Сервис уведомлений запущен (PID: {os.getpid()})")
        print(f"📁 Рабочая директория: {project_dir}")
        print(f"⏰ Интервал проверки: {self.check_interval} секунд")
        print("💡 Для остановки нажмите Ctrl+C или отправьте SIGTERM")
    
    def create_pid_file(self):
        """Создает файл с PID процесса"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print(f"Ошибка создания PID файла: {e}")
    
    def remove_pid_file(self):
        """Удаляет файл с PID процесса"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            print(f"Ошибка удаления PID файла: {e}")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print(f"\n🛑 Получен сигнал {signum}, завершаем работу...")
        self.running = False
        self.remove_pid_file()
        sys.exit(0)
    
    def play_notification_sound(self):
        """Воспроизводит звуковое оповещение"""
        try:
            if SOUND_AVAILABLE:
                # Получаем путь к файлу jink.mp3
                sound_path = get_sound_path("jink.mp3")
                if sound_path.exists():
                    pygame.mixer.music.load(str(sound_path))
                    pygame.mixer.music.play()
                else:
                    print(f"⚠️ Файл звука не найден: {sound_path}")
            else:
                # Fallback на системные звуки
                if sys.platform == "darwin":
                    os.system("say 'Внимание! Приближается дедлайн задачи!'")
                elif sys.platform.startswith("linux"):
                    os.system("espeak 'Attention! Task deadline approaching!'")
                elif sys.platform == "win32":
                    os.system("powershell -c \"[console]::beep(800,1000)\"")
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
    
    def show_system_notification(self, task):
        """Показывает системное уведомление"""
        try:
            # Для macOS всегда используем fallback, так как plyer требует pyobjus
            if sys.platform == "darwin":
                self.show_fallback_notification(task)
            elif NOTIFICATION_AVAILABLE:
                # Формируем текст уведомления
                title = f"⏰ TaskTide: {task['name']}"
                message = f"Осталось: {task['interval_name']}\nКатегория: {task['category2']}\nПриоритет: {task['category1']}"
                
                # Показываем системное уведомление
                notification.notify(
                    title=title,
                    message=message,
                    app_name="TaskTide",
                    timeout=10,  # Уведомление будет показано 10 секунд
                    toast=True
                )
            else:
                # Fallback для систем без plyer
                self.show_fallback_notification(task)
                
        except Exception as e:
            print(f"Ошибка показа системного уведомления: {e}")
            # Fallback на системные команды
            self.show_fallback_notification(task)
    
    def show_fallback_notification(self, task):
        """Fallback уведомления для систем без plyer"""
        try:
            title = f"TaskTide: {task['name']}"
            message = f"Осталось: {task['interval_name']}"
            
            if sys.platform == "darwin":  # macOS
                os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
            elif sys.platform.startswith("linux"):  # Linux
                os.system(f'notify-send "{title}" "{message}"')
            elif sys.platform == "win32":  # Windows
                os.system(f'powershell -c "[System.Windows.Forms.MessageBox]::Show(\'{message}\', \'{title}\', \'OK\', \'Warning\')"')
        except Exception as e:
            print(f"Ошибка fallback уведомления: {e}")
    
    def check_notifications(self):
        """Проверяет задачи, приближающиеся к дедлайну"""
        try:
            approaching_tasks = get_tasks_approaching_deadline()
            
            for task in approaching_tasks:
                # Создаем уникальный ключ для уведомления
                notification_key = f"{task['task_id']}_{task['interval_name']}"
                
                # Показываем уведомление только если его еще не показывали
                if notification_key not in self.shown_notifications:
                    print(f"🔔 Уведомление: {task['name']} - {task['interval_name']}")
                    
                    # Воспроизводим звуковое оповещение
                    self.play_notification_sound()
                    
                    # Показываем системное уведомление
                    self.show_system_notification(task)
                    
                    # Добавляем в список показанных уведомлений
                    self.shown_notifications.add(notification_key)
                    
        except Exception as e:
            print(f"Ошибка проверки уведомлений: {e}")
    
    def run(self):
        """Основной цикл сервиса"""
        print("🔄 Начинаем мониторинг задач...")
        
        while self.running:
            try:
                # Проверяем уведомления
                self.check_notifications()
                
                # Ждем до следующей проверки
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Получен сигнал прерывания")
                break
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
        
        print("✅ Сервис уведомлений завершен")

def is_service_running():
    """Проверяет, запущен ли сервис"""
    pid_file = get_runtime_file("notification_service.pid")
    if not pid_file.exists():
        return False
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Проверяем, существует ли процесс с таким PID
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Процесс не существует, удаляем PID файл
        try:
            pid_file.unlink()
        except:
            pass
        return False

def start_service():
    """Запускает сервис уведомлений"""
    if is_service_running():
        print("⚠️ Сервис уведомлений уже запущен")
        return
    
    print("🚀 Запускаем сервис уведомлений...")
    service = NotificationService()
    service.run()

def stop_service():
    """Останавливает сервис уведомлений"""
    pid_file = get_runtime_file("notification_service.pid")
    if not pid_file.exists():
        print("⚠️ Сервис уведомлений не запущен")
        return
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Отправляем сигнал SIGTERM
        os.kill(pid, signal.SIGTERM)
        print(f"🛑 Сервис уведомлений остановлен (PID: {pid})")
        
        # Удаляем PID файл
        pid_file.unlink()
        
    except (OSError, ValueError) as e:
        print(f"Ошибка остановки сервиса: {e}")

def status_service():
    """Показывает статус сервиса"""
    if is_service_running():
        try:
            with open(get_runtime_file("notification_service.pid"), 'r') as f:
                pid = f.read().strip()
            print(f"✅ Сервис уведомлений запущен (PID: {pid})")
        except:
            print("✅ Сервис уведомлений запущен")
    else:
        print("❌ Сервис уведомлений не запущен")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            start_service()
        elif command == "stop":
            stop_service()
        elif command == "status":
            status_service()
        elif command == "restart":
            stop_service()
            time.sleep(2)
            start_service()
        else:
            print("Использование: python3 notification_service.py [start|stop|status|restart]")
    else:
        # Запуск без аргументов - интерактивный режим
        start_service()
