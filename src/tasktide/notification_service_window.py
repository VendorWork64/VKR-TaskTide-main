#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервис уведомлений TaskTide с отдельными окнами
Показывает уведомления в виде отдельных окон вместо системных уведомлений
"""

import os
import sys
import time
import subprocess
import signal
from datetime import datetime, timedelta
import sqlite3
from src.tasktide.paths import get_db_path, get_runtime_file, get_sound_path

# Импорт для воспроизведения звука
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

# Импорт для создания окон уведомлений
try:
    from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QIcon
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    QWidget = object

class NotificationWindow(QWidget):
    """Окно уведомления о дедлайне"""
    
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса окна уведомления"""
        self.setWindowTitle("⏰ TaskTide - Уведомление о дедлайне")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(400, 200)
        
        # Центрируем окно на экране
        self.center_window()
        
        # Создаем макет
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel("⏰ ВНИМАНИЕ! Приближается дедлайн!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Информация о задаче
        task_info = f"""
        📋 Задача: {self.task['name']}
        ⏰ Осталось: {self.task['interval_name']}
        📂 Категория: {self.task['category2']}
        ⚡ Приоритет: {self.task['category1']}
        📊 Статус: {self.task['status']}
        """
        
        info_label = QLabel(task_info)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(info_label)
        
        # Кнопка закрытия
        close_btn = QPushButton("✓ Понятно")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Стиль окна
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #dc3545;
                border-radius: 10px;
            }
        """)
        
        # Автоматическое закрытие через 30 секунд
        self.timer = QTimer()
        self.timer.timeout.connect(self.close)
        self.timer.start(30000)  # 30 секунд
        
    def center_window(self):
        """Центрирует окно на экране"""
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

class NotificationService:
    """Сервис уведомлений с отдельными окнами"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Проверка каждые 60 секунд
        self.shown_notifications = set()  # Уже показанные уведомления
        
    def play_sound(self):
        """Воспроизводит звуковое уведомление"""
        try:
            if SOUND_AVAILABLE:
                # Получаем путь к файлу jink.mp3
                sound_path = str(get_sound_path("jink.mp3"))
                if os.path.exists(sound_path):
                    pygame.mixer.music.load(sound_path)
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
    
    def show_notification_window(self, task):
        """Показывает окно уведомления"""
        try:
            if GUI_AVAILABLE:
                # Создаем QApplication если его еще нет
                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)
                
                # Создаем новое окно уведомления
                notification_window = NotificationWindow(task)
                notification_window.show()
                
                # Воспроизводим звук
                self.play_sound()
                
                print(f"🔔 Показано окно уведомления: {task['name']} - {task['interval_name']}")
                
                # Обрабатываем события приложения
                app.processEvents()
                
            else:
                print("❌ PyQt5 недоступен для создания окон уведомлений")
                
        except Exception as e:
            print(f"Ошибка показа окна уведомления: {e}")
    
    def get_tasks_approaching_deadline(self):
        """Получает задачи, приближающиеся к дедлайну"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            now = datetime.now()
            
            # Определяем точные временные интервалы для уведомлений
            intervals = [
                (timedelta(hours=1), "1 час"),         # ровно 1 час
                (timedelta(hours=6), "6 часов"),       # ровно 6 часов
                (timedelta(hours=12), "12 часов"),     # ровно 12 часов
                (timedelta(days=1), "1 день"),        # ровно 1 день
                (timedelta(days=3), "3 дня"),         # ровно 3 дня
                (timedelta(days=7), "7 дней"),        # ровно 7 дней
                (timedelta(days=14), "2 недели"),     # ровно 2 недели
                (timedelta(days=30), "1 месяц")       # ровно 1 месяц
            ]
            
            approaching_tasks = []
            
            # Получаем все активные задачи (не выполненные)
            cursor.execute("""
                SELECT * FROM tasks
                WHERE status != 'выполнена'
                AND deadline IS NOT NULL
                AND deadline > ?
                ORDER BY deadline ASC
            """, (now,))
            
            tasks = cursor.fetchall()
            
            for task in tasks:
                task_id, name, category1, category2, deadline_str, status, description, created_at, updated_at = task
                
                try:
                    deadline = datetime.fromisoformat(deadline_str)
                    time_remaining = deadline - now
                    
                    # Проверяем каждый интервал на точное совпадение (с допуском в 5 минут)
                    tolerance = timedelta(minutes=5)  # Допуск в 5 минут для точности
                    
                    for interval, interval_name in intervals:
                        # Проверяем, находится ли оставшееся время в пределах интервала ± допуск
                        if abs(time_remaining - interval) <= tolerance:
                            approaching_tasks.append({
                                'task_id': task_id,
                                'name': name,
                                'category1': category1,
                                'category2': category2,
                                'deadline': deadline_str,
                                'status': status,
                                'description': description,
                                'time_remaining': time_remaining,
                                'interval_name': interval_name,
                                'interval_delta': interval
                            })
                            break  # Находим первое точное совпадение
                            
                except (ValueError, TypeError):
                    # Пропускаем задачи с некорректным форматом даты
                    continue
            
            conn.close()
            return approaching_tasks
            
        except Exception as e:
            print(f"Ошибка получения задач: {e}")
            return []
    
    def check_notifications(self):
        """Проверяет задачи и показывает уведомления"""
        try:
            approaching_tasks = self.get_tasks_approaching_deadline()
            
            for task in approaching_tasks:
                # Создаем уникальный ключ для уведомления
                notification_key = f"{task['task_id']}_{task['interval_name']}"
                
                # Показываем уведомление только если его еще не показывали
                if notification_key not in self.shown_notifications:
                    self.show_notification_window(task)
                    self.shown_notifications.add(notification_key)
                    
        except Exception as e:
            print(f"Ошибка проверки уведомлений: {e}")
    
    def start(self):
        """Запускает сервис уведомлений"""
        if self.running:
            print("⚠️ Сервис уведомлений уже запущен")
            return
            
        self.running = True
        print("🚀 Запускаем сервис уведомлений с окнами...")
        print(f"📁 Рабочая директория: {os.getcwd()}")
        print(f"⏰ Интервал проверки: {self.check_interval} секунд")
        print("💡 Для остановки нажмите Ctrl+C или отправьте SIGTERM")
        print("🔄 Начинаем мониторинг задач...")
        
        # Создаем QApplication для работы с окнами
        if GUI_AVAILABLE:
            app = QApplication(sys.argv)
            
            # Первоначальная проверка
            self.check_notifications()
            
            # Таймер для периодической проверки
            timer = QTimer()
            timer.timeout.connect(self.check_notifications)
            timer.start(self.check_interval * 1000)  # Конвертируем в миллисекунды
            
            # Обработчик сигналов для корректного завершения
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            
            try:
                app.exec_()
            except KeyboardInterrupt:
                self.stop()
        else:
            print("❌ PyQt5 недоступен. Сервис не может работать без GUI.")
    
    def stop(self):
        """Останавливает сервис уведомлений"""
        if not self.running:
            print("⚠️ Сервис уведомлений не запущен")
            return
            
        self.running = False
        print("🛑 Сервис уведомлений остановлен")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print(f"\n🛑 Получен сигнал {signum}, завершаем работу...")
        self.stop()
        sys.exit(0)

def is_service_running():
    """Проверяет, запущен ли сервис"""
    try:
        with open(str(get_runtime_file("notification_service_window.pid")), "r") as f:
            pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # Проверяем, существует ли процесс
                return True
            except OSError:
                return False
    except (FileNotFoundError, ValueError):
        return False

def start_service():
    """Запускает сервис в фоновом режиме"""
    if is_service_running():
        print("⚠️ Сервис уведомлений уже запущен")
        return
    
    # Запускаем сервис в фоновом режиме
    process = subprocess.Popen([
        sys.executable,
        __file__,
        "start"
    ], cwd=os.path.dirname(__file__))
    
    # Сохраняем PID
    with open(str(get_runtime_file("notification_service_window.pid")), "w") as f:
        f.write(str(process.pid))
    
    print(f"🚀 Сервис уведомлений запущен (PID: {process.pid})")

def stop_service():
    """Останавливает сервис"""
    if not is_service_running():
        print("⚠️ Сервис уведомлений не запущен")
        return
    
    try:
        with open(str(get_runtime_file("notification_service_window.pid")), "r") as f:
            pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            os.remove(str(get_runtime_file("notification_service_window.pid")))
            print(f"🛑 Сервис уведомлений остановлен (PID: {pid})")
    except (FileNotFoundError, ValueError, OSError) as e:
        print(f"Ошибка остановки сервиса: {e}")

def status_service():
    """Показывает статус сервиса"""
    if is_service_running():
        try:
            with open(str(get_runtime_file("notification_service_window.pid")), "r") as f:
                pid = int(f.read().strip())
                print(f"✅ Сервис уведомлений запущен (PID: {pid})")
        except (FileNotFoundError, ValueError):
            print("❌ Сервис уведомлений не запущен")
    else:
        print("❌ Сервис уведомлений не запущен")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
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
            print("Использование: python3 notification_service_window.py [start|stop|status|restart]")
    else:
        # Запуск без аргументов - интерактивный режим
        service = NotificationService()
        service.start()
