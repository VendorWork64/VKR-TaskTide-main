# ui5.py - Модуль Фокус с Pomodoro таймером

import sys
import os
from src.tasktide.paths import get_sound_path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QDialog, QListWidget, QListWidgetItem, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from src.tasktide.styles import get_default_style

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

# Импорт функций для работы с базой данных
from src.tasktide.database import get_focus_daily_stats, update_focus_daily_stats, add_focus_session

class FocusWindow(QMainWindow):
    """Главное окно модуля Фокус с Pomodoro таймером"""
    
    def __init__(self, show_main_menu_callback=None):
        super().__init__()
        self.show_main_menu_callback = show_main_menu_callback
        self.setWindowTitle("🎯 Фокус - Pomodoro Timer")
        self.setGeometry(100, 100, 800, 600)  # Уменьшаем размер окна
        self.setStyleSheet(get_default_style())
        
        # Pomodoro настройки
        self.pomodoro_duration = 25 * 60  # 25 минут в секундах
        self.short_break = 5 * 60  # 5 минут
        self.long_break = 25 * 60  # 25 минут длинный перерыв
        self.current_time = self.pomodoro_duration
        self.is_running = False
        self.is_break = False
        self.pomodoro_count = 0
        self.cycle_count = 0  # Счетчик циклов (максимум 4)
        self.total_pomodoros = 0  # Общее количество завершенных pomodoro
        
        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Выбранная задача
        self.selected_task = None
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)  # Уменьшаем отступы между секциями
        main_layout.setContentsMargins(15, 15, 15, 15)  # Меньше отступы от краев
        
        # Создаем интерфейс
        self.create_header(main_layout)
        self.create_pomodoro_section(main_layout)
        self.create_task_section(main_layout)
        
        # Инициализируем индикатор после создания интерфейса
        self.update_pomodoro_indicator()
        
        # Загружаем статистику при запуске
        self.load_daily_stats()
    
    def create_header(self, parent_layout):
        """Создает заголовок с кнопкой назад и статистикой"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)  # Уменьшаем отступы
        
        # Кнопка назад
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; padding: 6px 12px; font-weight: bold; font-size: 12px;")
        back_btn.setFixedSize(70, 35)  # Уменьшаем размер кнопки
        header_layout.addWidget(back_btn)
        
        # Статистика фокуса
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)  # Уменьшаем отступы
        
        # Статистика 1
        self.stats1 = QLabel("Время проведённое в фокусе за сегодня: 0ч 0мин")
        self.stats1.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; border-bottom: 1px solid #cfd9e5; padding: 8px; font-weight: bold; font-size: 14px;")
        self.stats1.setFixedHeight(40)  # Уменьшаем высоту
        stats_layout.addWidget(self.stats1)
        
        # Статистика 2
        self.stats2 = QLabel("Количество циклов проведённых в фокусе за сегодня: 0шт")
        self.stats2.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; border-bottom: 1px solid #cfd9e5; padding: 8px; font-weight: bold; font-size: 14px;")
        self.stats2.setFixedHeight(40)  # Уменьшаем высоту
        stats_layout.addWidget(self.stats2)
        
        header_layout.addLayout(stats_layout)
        parent_layout.addLayout(header_layout)
    
    def create_pomodoro_section(self, parent_layout):
        """Создает секцию с Pomodoro таймером"""
        pomodoro_frame = QFrame()
        pomodoro_frame.setStyleSheet("background-color: #cf3f2f; border: 1px solid #cfd9e5; border-radius: 10px;")
        pomodoro_frame.setFixedHeight(200)  # Значительно уменьшаем высоту
        pomodoro_layout = QVBoxLayout(pomodoro_frame)
        pomodoro_layout.setContentsMargins(15, 15, 15, 15)  # Уменьшаем отступы
        pomodoro_layout.setSpacing(10)  # Уменьшаем отступы
        
        # Верхняя панель с настройками и индикатором
        top_panel = QHBoxLayout()
        top_panel.setSpacing(10)  # Уменьшаем отступы
        
        # Иконки настроек (три элемента как на изображении)
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(5)  # Уменьшаем отступы
        
        # Кнопка выбора задач (гамбургер меню)
        self.task_select_btn = QPushButton("☰")
        self.task_select_btn.clicked.connect(self.show_task_selection)
        self.task_select_btn.setStyleSheet("color: white; font-size: 16px; background-color: rgba(255,255,255,0.2); border: 1px solid white; padding: 3px; border-radius: 2px;")
        self.task_select_btn.setFixedSize(30, 25)  # Уменьшаем ширину кнопки
        settings_layout.addWidget(self.task_select_btn)
        
        # Поле поиска задач
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск задач...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d9e2ec;
                padding: 5px;
                font-size: 12px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid #1f7a57;
            }
        """)
        self.search_input.setFixedSize(150, 25)
        self.search_input.textChanged.connect(self.search_tasks)
        settings_layout.addWidget(self.search_input)
        
        # Пустое место
        spacer = QWidget()
        spacer.setFixedWidth(30)  # Уменьшаем
        settings_layout.addWidget(spacer)
        
        top_panel.addLayout(settings_layout)
        
        # Индикатор Pomodoro
        self.pomodoro_indicator = QLabel("ПОМИДОР1 (1) →")
        self.pomodoro_indicator.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.pomodoro_indicator.setAlignment(Qt.AlignRight)
        top_panel.addWidget(self.pomodoro_indicator)
        
        pomodoro_layout.addLayout(top_panel)
        
        # Большой таймер
        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")  # Уменьшаем размер шрифта
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFixedHeight(60)  # Уменьшаем высоту для таймера
        pomodoro_layout.addWidget(self.timer_label)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Уменьшаем отступы для размещения 4 кнопок
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        self.reset_btn = QPushButton("СБРОС")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; padding: 8px 15px; font-weight: bold; font-size: 12px;")
        self.reset_btn.setFixedSize(90, 35)  # Уменьшаем размер кнопки
        buttons_layout.addWidget(self.reset_btn)
        
        self.start_btn = QPushButton("СТАРТ")
        self.start_btn.clicked.connect(self.start_timer)
        self.start_btn.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; padding: 8px 15px; font-weight: bold; font-size: 12px;")
        self.start_btn.setFixedSize(90, 35)  # Уменьшаем размер кнопки
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("СТОП")
        self.stop_btn.clicked.connect(self.stop_timer)
        self.stop_btn.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; padding: 8px 15px; font-weight: bold; font-size: 12px;")
        self.stop_btn.setFixedSize(90, 35)  # Уменьшаем размер кнопки
        buttons_layout.addWidget(self.stop_btn)
        
        self.skip_btn = QPushButton("ДАЛЕЕ")
        self.skip_btn.clicked.connect(self.skip_timer)
        self.skip_btn.setStyleSheet("background-color: #ffffff; color: #102a43; border: 1px solid #d9e2ec; padding: 8px 15px; font-weight: bold; font-size: 12px;")
        self.skip_btn.setFixedSize(90, 35)  # Уменьшаем размер кнопки
        buttons_layout.addWidget(self.skip_btn)
        
        pomodoro_layout.addLayout(buttons_layout)
        parent_layout.addWidget(pomodoro_frame)
    
    def create_task_section(self, parent_layout):
        """Создает секцию для отображения информации о выбранной задаче"""
        self.task_frame = QFrame()
        self.task_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #d9e2ec; border-radius: 10px;")
        self.task_frame.setFixedHeight(200)  # Сохраняем высоту
        self.task_layout = QVBoxLayout(self.task_frame)
        self.task_layout.setContentsMargins(10, 10, 10, 10)
        self.task_layout.setSpacing(8)
        
        # Инициализируем пустое поле
        self.update_task_display()

        parent_layout.addWidget(self.task_frame)
    
    def start_timer(self):
        """Запускает Pomodoro таймер"""
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)  # Обновление каждую секунду
            self.start_btn.setText("ПАУЗА")
        else:
            self.pause_timer()
    
    def pause_timer(self):
        """Приостанавливает таймер"""
        self.is_running = False
        self.timer.stop()
        self.start_btn.setText("СТАРТ")
    
    def stop_timer(self):
        """Останавливает таймер"""
        self.is_running = False
        self.timer.stop()
        self.is_break = False
        self.current_time = self.pomodoro_duration
        self.update_display()
        self.update_pomodoro_indicator()
        self.start_btn.setText("СТАРТ")
    
    def reset_timer(self):
        """Сбрасывает таймер к начальному состоянию"""
        self.is_running = False
        self.timer.stop()
        
        # Сбрасываем к начальному состоянию Pomodoro
        self.is_break = False
        self.current_time = self.pomodoro_duration
        self.pomodoro_count = 0
        self.cycle_count = 0
        
        self.update_display()
        self.update_pomodoro_indicator()
        self.start_btn.setText("СТАРТ")
        
        # Обновляем статистику (сброс не влияет на дневную статистику)
        self.load_daily_stats()
    
    def skip_timer(self):
        """Пропускает текущий этап и переходит к следующему"""
        self.is_running = False
        self.timer.stop()
        
        # Воспроизводим звуковое оповещение
        self.play_skip_sound()
        
        # Показываем системное уведомление о переходе
        self.show_skip_notification()
        
        if self.is_break:
            # Если сейчас перерыв, переходим к работе
            self.is_break = False
            self.current_time = self.pomodoro_duration
        else:
            # Если сейчас работа, переходим к перерыву
            self.is_break = True
            self.total_pomodoros += 1
            self.cycle_count += 1
            
            # Определяем тип перерыва
            if self.cycle_count >= 4:
                # Длинный перерыв после 4 циклов
                self.current_time = self.long_break
                self.cycle_count = 0  # Сбрасываем счетчик циклов
            else:
                # Короткий перерыв
                self.current_time = self.short_break
            
            # Обновляем статистику - завершен pomodoro
            self.update_stats_pomodoro_completed()
        
        self.update_display()
        self.update_pomodoro_indicator()
        self.start_btn.setText("СТАРТ")
    
    def update_timer(self):
        """Обновляет таймер каждую секунду"""
        if self.current_time > 0:
            self.current_time -= 1
            self.update_display()
        else:
            # Время истекло
            self.timer_finished()
    
    def update_display(self):
        """Обновляет отображение таймера"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def timer_finished(self):
        """Вызывается когда таймер завершился"""
        self.is_running = False
        self.timer.stop()
        
        # Воспроизводим звуковое уведомление
        self.play_notification_sound()
        
        if not self.is_break:
            # Завершился Pomodoro
            self.total_pomodoros += 1
            self.cycle_count += 1
            self.is_break = True
            
            # Определяем тип перерыва
            if self.cycle_count >= 4:
                # Длинный перерыв после 4 циклов
                self.current_time = self.long_break
                self.cycle_count = 0  # Сбрасываем счетчик циклов
            else:
                # Короткий перерыв
                self.current_time = self.short_break
                
            self.update_stats_pomodoro_completed()
        else:
            # Завершился перерыв - возвращаемся к работе
            self.is_break = False
            self.current_time = self.pomodoro_duration
        
        self.update_display()
        self.update_pomodoro_indicator()
        self.start_btn.setText("СТАРТ")
    
    def load_daily_stats(self):
        """Загружает статистику фокуса за сегодня из базы данных"""
        try:
            stats = get_focus_daily_stats()
            self.update_stats_display(stats)
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
            # Показываем нулевую статистику при ошибке
            self.update_stats_display({
                'total_focus_minutes': 0,
                'completed_cycles': 0
            })
    
    def update_stats_display(self, stats):
        """Обновляет отображение статистики"""
        total_minutes = stats['total_focus_minutes']
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        self.stats1.setText(f"Время проведённое в фокусе за сегодня: {hours}ч {minutes}мин")
        self.stats2.setText(f"Количество циклов проведённых в фокусе за сегодня: {stats['completed_cycles']}шт")
    
    def update_stats(self):
        """Обновляет статистику и сохраняет в базу данных"""
        # Сохраняем статистику в базу данных
        try:
            update_focus_daily_stats(
                focus_minutes=25,  # Один pomodoro = 25 минут
                completed_cycles=1,  # Один завершенный pomodoro = один цикл
                pomodoro_sessions=1
            )
            
            # Загружаем обновленную статистику
            self.load_daily_stats()
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
    
    def update_stats_pomodoro_completed(self):
        """Обновляет статистику при завершении pomodoro"""
        try:
            # Определяем тип перерыва для статистики
            if self.cycle_count >= 4:
                # Длинный перерыв
                update_focus_daily_stats(
                    focus_minutes=25,  # Один pomodoro = 25 минут
                    completed_cycles=1,  # Один завершенный pomodoro = один цикл
                    pomodoro_sessions=1,
                    long_breaks=1
                )
            else:
                # Короткий перерыв
                update_focus_daily_stats(
                    focus_minutes=25,  # Один pomodoro = 25 минут
                    completed_cycles=1,  # Один завершенный pomodoro = один цикл
                    pomodoro_sessions=1,
                    short_breaks=1
                )
            
            # Загружаем обновленную статистику
            self.load_daily_stats()
        except Exception as e:
            print(f"Ошибка сохранения статистики pomodoro: {e}")
    
    def play_notification_sound(self):
        """Воспроизводит звуковое уведомление"""
        try:
            # Для macOS используем say команду
            if sys.platform == "darwin":
                os.system("say 'Таймер завершен'")
            # Для Linux используем espeak
            elif sys.platform.startswith("linux"):
                os.system("espeak 'Timer finished'")
            # Для Windows используем PowerShell
            elif sys.platform == "win32":
                os.system("powershell -c \"[console]::beep(800,500)\"")
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
    
    def play_skip_sound(self):
        """Воспроизводит звуковое оповещение при пропуске этапа"""
        try:
            if SOUND_AVAILABLE:
                # Получаем путь к файлу jink.mp3
                sound_path = str(get_sound_path("jink.mp3"))
                if os.path.exists(sound_path):
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play()
                else:
                    print(f"Файл звука не найден: {sound_path}")
            else:
                # Fallback на системные звуки
                if sys.platform == "darwin":
                    os.system("say 'Этап пропущен'")
                elif sys.platform.startswith("linux"):
                    os.system("espeak 'Stage skipped'")
                elif sys.platform == "win32":
                    os.system("powershell -c \"[console]::beep(600,300)\"")
        except Exception as e:
            print(f"Ошибка воспроизведения звука пропуска: {e}")
    
    def show_skip_notification(self):
        """Показывает внутреннее уведомление о пропуске этапа"""
        try:
            # Определяем тип перехода
            if self.is_break:
                title = "🎯 Pomodoro: Начинаем работу"
                message = "Переход к рабочему времени (25 минут)"
            else:
                if self.cycle_count >= 4:
                    title = "☕ Pomodoro: Длинный перерыв"
                    message = "Переход к длинному перерыву (25 минут)"
                else:
                    title = "☕ Pomodoro: Короткий перерыв"
                    message = "Переход к небольшому перерыву"
            
            # Показываем внутреннее окно уведомления
            self.show_pomodoro_notification_window(title, message)
                
        except Exception as e:
            print(f"Ошибка показа уведомления пропуска: {e}")
    
    def show_pomodoro_notification_window(self, title, message):
        """Показывает внутреннее окно уведомления Pomodoro"""
        try:
            # Импортируем простую систему уведомлений
            from simple_notifications import show_notification
            
            # Показываем уведомление Pomodoro
            success = show_notification(title, message, "pomodoro")
            
            if success:
                print(f"🍅 Показано окно Pomodoro: {title}")
            else:
                # Fallback на диалог
                self.show_pomodoro_fallback_dialog(title, message)
            
        except Exception as e:
            print(f"Ошибка показа окна Pomodoro: {e}")
            # Fallback на диалог
            self.show_pomodoro_fallback_dialog(title, message)
    
    def show_pomodoro_fallback_dialog(self, title, message):
        """Fallback диалог для Pomodoro"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("🍅 TaskTide Pomodoro")
            msg_box.setText(f"{title}\n\n{message}")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)

            # Стилизация диалога
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f4f7fb;
                    border-radius: 10px;
                    border: 2px solid #2e7d32;
                }
                QMessageBox QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #1b5e20;
                }
            """)

            msg_box.exec_()
            
        except Exception as e:
            print(f"Ошибка fallback диалога Pomodoro: {e}")
    
    def update_pomodoro_indicator(self):
        """Обновляет индикатор Pomodoro"""
        if self.is_break:
            if self.current_time == self.long_break:
                self.pomodoro_indicator.setText("ДЛИННЫЙ ПЕРЕРЫВ →")
            else:
                self.pomodoro_indicator.setText("КОРОТКИЙ ПЕРЕРЫВ →")
        else:
            current_pomodoro = (self.cycle_count % 4) + 1
            self.pomodoro_indicator.setText(f"ПОМИДОР{current_pomodoro} ({self.cycle_count + 1}) →")
    
    def go_back(self):
        """Возвращается в главное меню"""
        if self.show_main_menu_callback:
            self.show_main_menu_callback()
    
    def show_task_selection(self):
        """Показывает диалог выбора задач"""
        dialog = TaskSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.selected_task = dialog.selected_task
            self.update_task_display()
    
    def search_tasks(self):
        """Поиск задач по названию"""
        search_text = self.search_input.text().lower().strip()
        
        if not search_text:
            # Если поле поиска пустое, показываем пустое поле
            self.update_task_display()
            return
        
        try:
            # Импортируем функцию для получения задач
            from src.tasktide.database import get_all_tasks
            tasks = get_all_tasks()
            
            # Ищем задачи по названию
            matching_tasks = []
            for task in tasks:
                task_name = task[1].lower()  # Название задачи
                if search_text in task_name:
                    # Формируем объект задачи
                    task_obj = {
                        'id': task[0],
                        'name': task[1],
                        'description': task[6] if len(task) > 6 else "Описание не указано",
                        'time': self.calculate_time_remaining(task[4]),
                        'priority': task[2],
                        'category': task[3],
                        'status': task[5],
                        'deadline': task[4]
                    }
                    matching_tasks.append(task_obj)
            
            if matching_tasks:
                # Показываем первую найденную задачу
                self.selected_task = matching_tasks[0]
                self.update_task_display()
            else:
                # Если ничего не найдено, показываем сообщение
                self.show_no_results_message()
                
        except Exception as e:
            print(f"Ошибка поиска задач: {e}")
            self.show_no_results_message()
    
    def calculate_time_remaining(self, deadline):
        """Вычисляет оставшееся время до дедлайна"""
        if not deadline:
            return "Время не указано"
        
        try:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(deadline)
            now = datetime.now()
            
            if deadline_dt < now:
                return "🔴 Просрочено"
            else:
                delta = deadline_dt - now
                if delta.days > 0:
                    return f"🟡 {delta.days}д"
                elif delta.seconds // 3600 > 0:
                    return f"🟡 {delta.seconds // 3600}ч"
                else:
                    return f"🟢 {delta.seconds // 60}м"
        except:
            return "Время не указано"
    
    def show_no_results_message(self):
        """Показывает сообщение о том, что задачи не найдены"""
        # Очищаем layout
        for i in reversed(range(self.task_layout.count())):
            self.task_layout.itemAt(i).widget().setParent(None)
        
        # Показываем сообщение
        no_results_label = QLabel("🔍 Задачи не найдены")
        no_results_label.setAlignment(Qt.AlignCenter)
        no_results_label.setStyleSheet("font-size: 16px; color: gray;")
        self.task_layout.addWidget(no_results_label)
    
    def update_task_display(self):
        """Обновляет отображение информации о задаче"""
        # Очищаем layout
        for i in reversed(range(self.task_layout.count())):
            self.task_layout.itemAt(i).widget().setParent(None)
        
        if self.selected_task:
            # Отображаем информацию о выбранной задаче
            self.display_task_info()
        else:
            # Отображаем пустое поле
            empty_label = QLabel("Пустое поле для задач")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 16px; color: gray;")
            self.task_layout.addWidget(empty_label)
    
    def display_task_info(self):
        """Отображает детальную информацию о выбранной задаче"""
        if not self.selected_task:
            return
        
        # Название задачи
        title_label = QLabel(f"📋 {self.selected_task['name']}")
        title_label.setStyleSheet("font-size: 14px; color: #102a43;")
        title_label.setFixedHeight(30)
        self.task_layout.addWidget(title_label)
        
        # Описание задачи
        if self.selected_task.get('description'):
            desc_label = QLabel(f"📝 Описание: {self.selected_task['description']}")
            desc_label.setStyleSheet("font-size: 14px; color: #102a43;")
            desc_label.setFixedHeight(30)
            desc_label.setWordWrap(True)
            self.task_layout.addWidget(desc_label)
        
        # Категория и приоритет
        category_label = QLabel(f"🏷️ Категория: {self.selected_task.get('category', 'Не указана')}")
        category_label.setStyleSheet("font-size: 14px; color: #102a43;")
        category_label.setFixedHeight(30)
        self.task_layout.addWidget(category_label)
        
        priority_label = QLabel(f"⚡ Приоритет: {self.selected_task.get('priority', 'Не указан')}")
        priority_label.setStyleSheet("font-size: 14px; color: #102a43;")
        priority_label.setFixedHeight(30)
        self.task_layout.addWidget(priority_label)
        
        # Статус
        status_label = QLabel(f"📊 Статус: {self.selected_task.get('status', 'Не указан')}")
        status_label.setStyleSheet("font-size: 14px; color: #102a43;")
        status_label.setFixedHeight(30)
        self.task_layout.addWidget(status_label)
        
        # Время до истечения срока
        time_label = QLabel(f"⏰ Время до истечения: {self.selected_task.get('time', 'Не указано')}")
        time_label.setStyleSheet("font-size: 14px; color: #102a43;")
        time_label.setFixedHeight(30)
        self.task_layout.addWidget(time_label)


class TaskSelectionDialog(QDialog):
    """Диалог выбора задач"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_task = None
        self.setWindowTitle("Выбор задачи")
        self.setGeometry(200, 200, 500, 600)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("📋 Выберите задачу:")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Список задач
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                font-size: 14px; 
                padding: 5px;
                border: 1px solid #d9e2ec;
                background-color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
            }
        """)
        self.task_list.itemDoubleClicked.connect(self.select_task)
        layout.addWidget(self.task_list)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ Выбрать")
        select_btn.clicked.connect(self.select_task)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50; 
                color: white; 
                border: 2px solid #2e7d32; 
                padding: 10px 20px; 
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                border: 2px solid #c62828; 
                padding: 10px 20px; 
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Загружаем задачи
        self.load_tasks()
    
    def load_tasks(self):
        """Загружает список задач из базы данных"""
        self.task_list.clear()
        
        try:
            # Импортируем функцию для получения задач
            from src.tasktide.database import get_all_tasks
            tasks = get_all_tasks()
            
            if not tasks:
                item = QListWidgetItem("📝 Задач пока нет")
                item.setTextAlignment(Qt.AlignCenter)
                item.setStyleSheet("color: gray; font-style: italic;")
                self.task_list.addItem(item)
                return
            
            for task in tasks:
                # task = (id, name, category1, category2, deadline, status, description, created_at, updated_at)
                task_id = task[0]
                task_name = task[1]
                task_priority = task[2]  # category1 - приоритет
                task_category = task[3]  # category2 - категория
                task_deadline = task[4]
                task_status = task[5]
                task_description = task[6] if len(task) > 6 else "Описание не указано"
                
                # Формируем информацию о времени
                time_info = "Время не указано"
                if task_deadline:
                    try:
                        from datetime import datetime
                        deadline = datetime.fromisoformat(task_deadline)
                        now = datetime.now()
                        if deadline < now:
                            time_info = "🔴 Просрочено"
                        else:
                            delta = deadline - now
                            if delta.days > 0:
                                time_info = f"🟡 {delta.days}д"
                            elif delta.seconds // 3600 > 0:
                                time_info = f"🟡 {delta.seconds // 3600}ч"
                            else:
                                time_info = f"🟢 {delta.seconds // 60}м"
                    except:
                        time_info = "Время не указано"
                
                # Создаем объект задачи для передачи
                task_obj = {
                    'id': task_id,
                    'name': task_name,
                    'description': task_description,
                    'time': time_info,
                    'priority': task_priority,
                    'category': task_category,
                    'status': task_status,
                    'deadline': task_deadline
                }
                
                # Формируем текст для отображения
                item_text = f"📋 {task_name}\n🏷️ {task_category} | ⚡ {task_priority} | {time_info}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, task_obj)
                
                # Цветовое кодирование по статусу
                if task_status == 'выполнена':
                    item.setBackground(Qt.green)
                elif task_status == 'в процессе':
                    item.setBackground(Qt.yellow)
                elif task_status == 'просрочено' or (task_deadline and "Просрочено" in time_info):
                    item.setBackground(Qt.red)
                
                self.task_list.addItem(item)
                
        except Exception as e:
            item = QListWidgetItem(f"❌ Ошибка загрузки задач: {str(e)}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setStyleSheet("color: red; font-weight: bold;")
            self.task_list.addItem(item)
    
    def select_task(self):
        """Выбирает задачу"""
        current_item = self.task_list.currentItem()
        if current_item:
            self.selected_task = current_item.data(Qt.UserRole)
            self.accept()
