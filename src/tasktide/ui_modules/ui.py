# ui.py

from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QStackedWidget, QHBoxLayout, QLabel, QMessageBox, QGridLayout, QDialog, QComboBox, QLineEdit, QSpinBox, QListWidgetItem, QMenu, QInputDialog, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QTimer
import sqlite3
from src.tasktide.paths import get_db_path
from datetime import datetime, timedelta
import os
from src.tasktide.paths import get_sound_path
import sys

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

from src.tasktide.styles import get_default_style, get_dark_theme_style, get_main_menu_button_style, get_button_style, get_theme_button_style
from src.tasktide.ui2 import TaskListView  # Импортируем класс для списка задач
from src.tasktide.ui3 import NotesView  # Импортируем класс для заметок
from src.tasktide.ui4 import StatisticsWindow  # Импортируем класс для статистики
from src.tasktide.ui5 import FocusWindow  # Импортируем класс для фокуса
from src.tasktide.database import get_tasks_statistics  # Импортируем функцию статистики

class AddTaskDialog(QDialog):
    def __init__(self, style, step_number=1, total_steps=5):
        super().__init__()
        self.setStyleSheet(style)
        self.setWindowTitle(f"{step_number}/{total_steps} ✨ Добавить задачу")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4f7fb, stop:1 #eef3f9);
                border-radius: 15px;
                border: 2px solid #d9e2ec;
            }
            QLabel {
                color: #102a43;
                font-size: 18px;
                font-weight: 600;
                padding: 8px;
                background: transparent;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                color: #495057;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
                border-color: #1f7a57;
                border-width: 3px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #486581;
                margin-right: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f7a57, stop:1 #176547);
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #176547, stop:1 #0f5137);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f5137, stop:1 #002752);
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Кнопка для перехода к следующему шагу
        self.next_button = QPushButton("Далее →")
        self.next_button.clicked.connect(self.next_step)

        self.layout.addWidget(self.next_button)
        self.setLayout(self.layout)

    def next_step(self):
        pass

class Category1Dialog(AddTaskDialog):
    def __init__(self, style):
        super().__init__(style, step_number=1, total_steps=5)
        
        title_label = QLabel("🎯 Выберите приоритет задачи")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #102a43;
            text-align: center;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 123, 255, 0.1), stop:1 rgba(0, 123, 255, 0.05));
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Используй Матрицу Эйзенхауэра")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #486581;
            text-align: center;
            padding: 5px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        self.category1_combo = QComboBox()
        self.category1_combo.addItems([
            "🔥 Важно - Срочно",
            "⭐ Важно - Не срочно", 
            "⚡ Не важно - Срочно",
            "📝 Не важно - Не срочно"
        ])
        
        self.layout.insertWidget(0, title_label)
        self.layout.insertWidget(1, subtitle_label)
        self.layout.insertWidget(2, self.category1_combo)

    def next_step(self):
        category1 = self.category1_combo.currentText()
        self.close()
        dialog = Category2Dialog(category1, self.styleSheet())
        dialog.exec_()

class Category2Dialog(AddTaskDialog):
    def __init__(self, category1, style):
        super().__init__(style, step_number=2, total_steps=5)
        self.category1 = category1
        
        title_label = QLabel("📂 Выберите категорию задачи")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #102a43;
            text-align: center;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(40, 167, 69, 0.1), stop:1 rgba(40, 167, 69, 0.05));
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        self.category2_combo = QComboBox()
        self.category2_combo.addItems([
            "💼 Работа", 
            "📚 Учёба", 
            "👤 Личное"
        ])
        
        self.layout.insertWidget(0, title_label)
        self.layout.insertWidget(1, self.category2_combo)

    def next_step(self):
        category2 = self.category2_combo.currentText()
        self.close()
        dialog = DeadlineDialog(self.category1, category2, self.styleSheet())
        dialog.exec_()

class DeadlineDialog(AddTaskDialog):
    def __init__(self, category1, category2, style):
        super().__init__(style, step_number=3, total_steps=5)
        self.category1 = category1
        self.category2 = category2

        title_label = QLabel("⏰ Установите время выполнения")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #102a43;
            text-align: center;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 193, 7, 0.1), stop:1 rgba(255, 193, 7, 0.05));
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Укажите время для выполнения задачи")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #486581;
            text-align: center;
            padding: 5px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)

        time_layout = QHBoxLayout()
        
        self.time_input = QLineEdit()
        self.time_input.setText("30")
        self.time_input.setPlaceholderText("Введите число")
        self.time_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #ced4da;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                color: #495057;
                min-height: 20px;
                min-width: 100px;
            }
            QLineEdit:focus {
                border-color: #1f7a57;
                border-width: 3px;
            }
        """)
        
        self.time_unit_combo = QComboBox()
        self.time_unit_combo.addItems([
            "минут", 
            "часов", 
            "дней", 
            "недель",
            "месяцев", 
            "лет"
        ])
        self.time_unit_combo.setCurrentText("минут")
        
        time_layout.addWidget(self.time_input)
        time_layout.addWidget(self.time_unit_combo)
        time_layout.setSpacing(10)

        self.layout.insertWidget(0, title_label)
        self.layout.insertWidget(1, subtitle_label)
        self.layout.insertWidget(2, QWidget())  # Placeholder для layout
        self.layout.itemAt(2).widget().setLayout(time_layout)

    def next_step(self):
        time_text = self.time_input.text().strip()
        
        # Проверяем, что введено число
        try:
            time_value = int(time_text)
            if time_value <= 0:
                QMessageBox.warning(self, "Ошибка", "Время должно быть положительным числом!")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректное число!")
            return
            
        time_unit = self.time_unit_combo.currentText()
        
        # Конвертация в минуты
        if time_unit == "минут":
            minutes = time_value
        elif time_unit == "часов":
            minutes = time_value * 60
        elif time_unit == "дней":
            minutes = time_value * 60 * 24
        elif time_unit == "недель":
            minutes = time_value * 60 * 24 * 7
        elif time_unit == "месяцев":
            minutes = time_value * 60 * 24 * 30  # Приблизительно 30 дней в месяце
        elif time_unit == "лет":
            minutes = time_value * 60 * 24 * 365  # Приблизительно 365 дней в году
        else:
            minutes = time_value
            
        self.close()
        dialog = TaskNameDialog(self.category1, self.category2, minutes, self.styleSheet())
        dialog.exec_()

class TaskNameDialog(AddTaskDialog):
    def __init__(self, category1, category2, minutes, style):
        super().__init__(style, step_number=4, total_steps=5)
        self.category1 = category1
        self.category2 = category2
        self.minutes = minutes
        
        title_label = QLabel("✏️ Название задачи")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #102a43;
            text-align: center;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(220, 53, 69, 0.1), stop:1 rgba(220, 53, 69, 0.05));
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Введите краткое и понятное название (до 20 символов)")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #486581;
            text-align: center;
            padding: 5px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(20)
        self.name_input.setPlaceholderText("Например: Написать отчет")
        
        self.layout.insertWidget(0, title_label)
        self.layout.insertWidget(1, subtitle_label)
        self.layout.insertWidget(2, self.name_input)

    def next_step(self):
        name = self.name_input.text()
        if not name.strip():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название задачи!")
            return
        self.close()
        dialog = TaskDescriptionDialog(self.category1, self.category2, self.minutes, name, self.styleSheet())
        dialog.exec_()

class TaskDescriptionDialog(AddTaskDialog):
    def __init__(self, category1, category2, minutes, name, style):
        super().__init__(style, step_number=5, total_steps=5)
        self.category1 = category1
        self.category2 = category2
        self.minutes = minutes
        self.name = name
        
        title_label = QLabel("📋 Описание задачи")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #102a43;
            text-align: center;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(111, 66, 193, 0.1), stop:1 rgba(111, 66, 193, 0.05));
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Добавьте подробное описание задачи (необязательно)")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #486581;
            text-align: center;
            padding: 5px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Подробное описание задачи...")
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                color: #495057;
            }
            QTextEdit:focus {
                border-color: #1f7a57;
            }
        """)

        # Изменяем текст кнопки на "Сохранить"
        self.next_button.setText("💾 Сохранить задачу")
        self.next_button.clicked.disconnect()
        self.next_button.clicked.connect(self.save_task)

        self.layout.insertWidget(0, title_label)
        self.layout.insertWidget(1, subtitle_label)
        self.layout.insertWidget(2, self.description_input)

    def save_task(self):
        description = self.description_input.toPlainText()
        save_task(self.name, self.category1, self.category2, self.minutes, description)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("✅ Успех!")
        msg.setText("Задача успешно добавлена!")
        msg.setInformativeText(f"Задача '{self.name}' была сохранена в категории '{self.category2}'")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f4f7fb;
                border-radius: 10px;
            }
            QMessageBox QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        msg.exec_()
        self.accept()

def save_task(name, category1, category2, minutes, description):
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    # Вычисляем deadline как текущее время + указанные минуты
    deadline = datetime.now() + timedelta(minutes=minutes)
    
    cursor.execute('''
        INSERT INTO tasks (name, category1, category2, deadline, description, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (name, category1, category2, deadline, description, 'не начата'))
    conn.commit()
    conn.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Установка заголовка и фиксированных размеров окна
        self.setWindowTitle("TaskTide - Менеджер задач")
        self.setFixedSize(800, 600)  # Фиксированный размер окна

        # Центральный виджет и его компоновка
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Стек для различных представлений
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # Главное меню
        self.main_menu = QWidget()
        self.main_layout = QGridLayout()
        self.main_menu.setLayout(self.main_layout)

        # Добавление заголовка в главное меню
        title_label = QLabel("Take Tide Tracker")
        title_label.setStyleSheet("""
            font-size: 80px;
            font-weight: bold;
            padding: 10px;
            color: #2c4875;  /* Цвет текста заголовка */
        """)
        title_label.setAlignment(Qt.AlignCenter)  # Выравнивание по центру
        self.main_layout.addWidget(title_label, 0, 0, 1, 2)  # Добавление заголовка в первую строку

        # Добавление главного меню в стек
        self.stack.addWidget(self.main_menu)

        # Кнопки главного меню
        self.btn_tasks = QPushButton("Задачи")
        self.btn_tasks.clicked.connect(self.show_tasks)

        self.btn_notes = QPushButton("Подзадачи")
        self.btn_notes.clicked.connect(self.show_notes)  # Добавляем обработчик для заметок
        
        self.btn_statistics = QPushButton("Статистика")
        self.btn_statistics.clicked.connect(self.show_statistics)  # Добавляем обработчик для статистики
        
        self.btn_focus = QPushButton("Фокус")
        self.btn_focus.clicked.connect(self.show_focus)  # Добавляем обработчик для фокуса

        # Применение стилей к кнопкам главного меню
        for btn in [self.btn_tasks, self.btn_notes, self.btn_statistics, self.btn_focus]:
            btn.setStyleSheet(get_main_menu_button_style())

        # Добавление кнопок в компоновку главного меню
        self.main_layout.addWidget(self.btn_tasks, 1, 0)
        self.main_layout.addWidget(self.btn_notes, 1, 1)
        self.main_layout.addWidget(self.btn_statistics, 2, 0)
        self.main_layout.addWidget(self.btn_focus, 2, 1)

        # Кнопка переключения темы (темная/светлая)
        self.theme_toggle = QPushButton("☀")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setStyleSheet(get_theme_button_style())
        self.theme_toggle.clicked.connect(self.toggle_theme)

        # Добавление кнопки переключения темы в нижний правый угол
        self.layout.addWidget(self.theme_toggle, alignment=Qt.AlignBottom | Qt.AlignRight)

        # Вид для задач
        self.tasks_view = QWidget()
        self.tasks_layout = QVBoxLayout()
        self.tasks_view.setLayout(self.tasks_layout)
        self.stack.addWidget(self.tasks_view)

        # Настройка представления задач
        self.setup_tasks_view()

        # Создание экземпляра TaskListView
        self.task_list_view = TaskListView(self.show_tasks)  # Передаем метод show_tasks в качестве аргумента
        self.stack.addWidget(self.task_list_view)
        
        # Создание экземпляра NotesView
        self.notes_view = NotesView(self.show_main_menu)  # Передаем метод show_main_menu в качестве аргумента
        self.stack.addWidget(self.notes_view)
        
        # Создание экземпляра StatisticsWindow
        self.statistics_window = StatisticsWindow(self.show_main_menu)
        self.stack.addWidget(self.statistics_window)

        # Настройка представления плана
        self.setup_plan_view()

        # Настройка представления статистики
        self.setup_statistics_view()

        # Настройка представления инструкций
        self.setup_focus_view()

        # Инициализация системы уведомлений
        self.setup_notification_system()

        self.setStyleSheet(get_default_style())

    def setup_tasks_view(self):
        # Создание заголовка
        header = QLabel("Управление задачами")

        # Применение стилей к заголовку
        header.setStyleSheet("""
            font-size: 50px;
            font-weight: bold;
            padding: 10px;
            color: #e5c185;  /* Оранжево-красный цвет */
        """)

        # Выравнивание текста по центру
        header.setAlignment(Qt.AlignCenter)

        # Добавление заголовка в макет
        self.tasks_layout.addWidget(header)

        # Кнопка для добавления задачи
        btn_add_task = QPushButton("Добавить задачу")
        btn_add_task.clicked.connect(self.open_add_task_dialog)
        btn_add_task.setStyleSheet(get_button_style())

        # Кнопка для просмотра задач
        btn_view_tasks = QPushButton("Список задач")
        btn_view_tasks.clicked.connect(self.show_task_list)  # Переход к списку задач
        btn_view_tasks.setStyleSheet(get_button_style())

        # Компоновка для кнопок задач
        task_buttons_layout = QHBoxLayout()
        task_buttons_layout.setSpacing(20)  # Минимум расстояния между кнопками
        task_buttons_layout.setContentsMargins(1, 1, 1, 1)  # Убираем отступы
        task_buttons_layout.addWidget(btn_add_task)
        task_buttons_layout.addWidget(btn_view_tasks)

        # Центрируем кнопки
        task_buttons_layout.setAlignment(Qt.AlignCenter)

        # Добавление компоновки кнопок в вид задач
        self.tasks_layout.addLayout(task_buttons_layout)

        # Кнопка "Назад" для возврата в главное меню
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_main_menu)
        back_button.setStyleSheet(get_button_style())
        self.tasks_layout.addWidget(back_button, alignment=Qt.AlignCenter)  # Центрируем кнопку "Назад"

    def setup_plan_view(self):
        """Настройка представления плана"""
        self.plan_view = QWidget()
        plan_layout = QVBoxLayout()
        self.plan_view.setLayout(plan_layout)
        
        # Заголовок
        header = QLabel("Планирование задач")
        header.setStyleSheet("""
            font-size: 50px;
            font-weight: bold;
            padding: 10px;
            color: #102a43;
        """)
        header.setAlignment(Qt.AlignCenter)
        plan_layout.addWidget(header)
        
        # Информация о планировании
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <h3>Матрица Эйзенхауэра для планирования:</h3>
        <ul>
            <li><b>Важно - Срочно:</b> Кризисы, срочные проблемы</li>
            <li><b>Важно - Не срочно:</b> Планирование, развитие, профилактика</li>
            <li><b>Не важно - Срочно:</b> Прерывания, некоторые звонки</li>
            <li><b>Не важно - Не срочно:</b> Развлечения, пустая трата времени</li>
        </ul>
        <p>Рекомендуется сосредоточиться на квадранте "Важно - Не срочно" для достижения долгосрочных целей.</p>
        """)
        plan_layout.addWidget(info_text)
        
        # Кнопка назад
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_main_menu)
        back_button.setStyleSheet(get_button_style())
        plan_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.stack.addWidget(self.plan_view)

    def setup_statistics_view(self):
        """Настройка представления статистики"""
        self.statistics_view = QWidget()
        stats_layout = QVBoxLayout()
        self.statistics_view.setLayout(stats_layout)
        
        # Заголовок
        header = QLabel("Статистика задач")
        header.setStyleSheet("""
            font-size: 50px;
            font-weight: bold;
            padding: 10px;
            color: #102a43;
        """)
        header.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(header)
        
        # Область для отображения статистики
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            font-size: 18px;
            padding: 20px;
            background-color: #d7f9f8;
            border: 2px solid #d9e2ec;
            border-radius: 8px;
            margin: 10px;
            color: #2c4875;
        """)
        self.stats_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.stats_label)
        
        # Кнопка обновления статистики
        refresh_button = QPushButton("Обновить статистику")
        refresh_button.clicked.connect(self.update_statistics)
        refresh_button.setStyleSheet(get_button_style())
        stats_layout.addWidget(refresh_button, alignment=Qt.AlignCenter)
        
        # Кнопка назад
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_main_menu)
        back_button.setStyleSheet(get_button_style())
        stats_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.stack.addWidget(self.statistics_view)

    def setup_focus_view(self):
        """Настройка представления фокуса"""
        # Создаем экземпляр FocusWindow
        self.focus_window = FocusWindow(self.show_main_menu)
        self.stack.addWidget(self.focus_window)

    def show_task_list(self):
        # Отображение списка задач
        self.stack.setCurrentWidget(self.task_list_view)

    def open_add_task_dialog(self):
        current_style = get_dark_theme_style() if self.theme_toggle.isChecked() else get_default_style()
        dialog = Category1Dialog(current_style)
        dialog.exec_()

    def show_tasks(self):
        # Отображение представления задач
        self.stack.setCurrentWidget(self.tasks_view)

    def show_main_menu(self):
        # Возврат к главному меню
        self.stack.setCurrentWidget(self.main_menu)

    def toggle_theme(self):
        # Переключение между темной и светлой темами
        if self.theme_toggle.isChecked():
            self.setStyleSheet(get_dark_theme_style())
            self.theme_toggle.setText("☾")
            self.update_header_colors("#b8c5d1")  # Светлый цвет для тёмной темы
            # Обновляем стили списка задач для тёмной темы
            if hasattr(self, 'task_list_view'):
                self.task_list_view.update_theme_styles(True)
        else:
            self.setStyleSheet(get_default_style())
            self.theme_toggle.setText("☀")
            self.update_header_colors("#e5c185")  # Оранжевый цвет для светлой темы
            # Обновляем стили списка задач для светлой темы
            if hasattr(self, 'task_list_view'):
                self.task_list_view.update_theme_styles(False)
    
    def update_header_colors(self, color):
        """Обновляет цвета всех заголовков в зависимости от темы"""
        # Главный заголовок
        title_label = self.main_layout.itemAtPosition(0, 0).widget()
        if title_label:
            title_label.setStyleSheet(f"""
                font-size: 80px;
                font-weight: bold;
                padding: 10px;
                color: {color};
            """)
        
        # Заголовки в различных разделах
        headers = [
            self.tasks_layout.itemAt(0).widget(),  # Заголовок "Управление задачами"
            self.plan_view.layout().itemAt(0).widget(),
            self.statistics_view.layout().itemAt(0).widget(),
        ]

        for header in headers:
            if header and hasattr(header, 'setStyleSheet'):
                header.setStyleSheet(f"""
                    font-size: 50px;
                    font-weight: bold;
                    padding: 10px;
                    color: {color};
                """)

    def show_plan(self):
        """Отображение представления плана"""
        self.stack.setCurrentWidget(self.plan_view)

    def show_notes(self):
        """Отображение представления заметок"""
        self.stack.setCurrentWidget(self.notes_view)

    def show_statistics(self):
        """Отображение представления статистики"""
        self.stack.setCurrentWidget(self.statistics_window)

    def show_focus(self):
        """Отображение окна фокуса"""
        self.stack.setCurrentWidget(self.focus_window)

    def update_statistics(self):
        """Обновление статистики"""
        stats = get_tasks_statistics()
        stats_text = f"""
        <h3>Общая статистика:</h3>
        <p><b>Всего задач:</b> {stats['total']}</p>
        <p><b>Выполнено:</b> {stats['completed']}</p>
        <p><b>В процессе:</b> {stats['in_progress']}</p>
        <p><b>Не начато:</b> {stats['not_started']}</p>
        """
        
        if stats['total'] > 0:
            completion_rate = (stats['completed'] / stats['total']) * 100
            stats_text += f"<p><b>Процент выполнения:</b> {completion_rate:.1f}%</p>"
        
        self.stats_label.setText(stats_text)
    
    def setup_notification_system(self):
        """Настройка системы уведомлений о приближающихся дедлайнах"""
        # Таймер для проверки уведомлений каждые 15 секунд
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_deadline_notifications)
        self.notification_timer.start(15 * 1000)  # 15 секунд в миллисекундах
        
        # Список уже показанных уведомлений (чтобы не повторять)
        self.shown_notifications = set()
        
        # Первоначальная проверка при запуске
        self.check_deadline_notifications()
    
    def check_deadline_notifications(self):
        """Проверяет задачи, приближающиеся к дедлайну, и показывает уведомления"""
        try:
            from src.tasktide.database import get_tasks_approaching_deadline
            approaching_tasks = get_tasks_approaching_deadline()
            
            print(f"🔍 Проверка дедлайнов: найдено {len(approaching_tasks)} задач")
            
            for task in approaching_tasks:
                # Создаем уникальный ключ для уведомления
                notification_key = f"{task['task_id']}_{task['interval_name']}"
                
                # Показываем уведомление только если его еще не показывали
                if notification_key not in self.shown_notifications:
                    print(f"🔔 Новое уведомление: {task['name']} - {task['interval_name']}")
                    self.show_deadline_notification(task)
                    self.shown_notifications.add(notification_key)
                else:
                    print(f"⏭️ Уведомление уже показано: {task['name']} - {task['interval_name']}")
                    
        except Exception as e:
            print(f"Ошибка проверки уведомлений: {e}")
    
    def show_deadline_notification(self, task):
        """Показывает уведомление о приближающемся дедлайне"""
        # Воспроизводим звуковое оповещение
        self.play_task_notification_sound()

        # Показываем отдельное окно уведомления
        self.show_notification_window(task)

    def show_notification_window(self, task):
        """Показывает отдельное окно уведомления"""
        try:
            # Импортируем простую систему уведомлений
            from simple_notifications import show_notification
            
            # Формируем заголовок и сообщение
            title = "ВНИМАНИЕ! Приближается дедлайн!"
            message = f"""📋 Задача: {task['name']}
⏰ Осталось: {task['interval_name']}
📂 Категория: {task['category2']}
⚡ Приоритет: {task['category1']}
📊 Статус: {task['status']}"""
            
            # Показываем уведомление
            success = show_notification(title, message, "deadline")
            
            if success:
                print(f"🔔 Показано окно уведомления: {task['name']} - {task['interval_name']}")
            else:
                # Fallback на диалог
                self.show_fallback_dialog(task)
            
        except Exception as e:
            print(f"Ошибка показа окна уведомления: {e}")
            # Fallback на диалог
            self.show_fallback_dialog(task)
    
    def show_fallback_dialog(self, task):
        """Fallback диалог уведомления"""
        try:
            message = f"""
            ⏰ ВНИМАНИЕ! Приближается дедлайн!

            📋 Задача: {task['name']}
            ⏰ Осталось: {task['interval_name']}
            📂 Категория: {task['category2']}
            ⚡ Приоритет: {task['category1']}
            📊 Статус: {task['status']}

            Не забудьте выполнить задачу!
            """

            # Показываем диалог уведомления
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("⏰ Уведомление о дедлайне")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Ok)

            # Стилизация диалога
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f4f7fb;
                    border-radius: 10px;
                    border: 2px solid #cf3f2f;
                }
                QMessageBox QPushButton {
                    background-color: #cf3f2f;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #c82333;
                }
            """)

            msg_box.exec_()
            
        except Exception as e:
            print(f"Ошибка fallback диалога: {e}")
    
    
    def play_task_notification_sound(self):
        """Воспроизводит звуковое оповещение для задач"""
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
                    os.system("say 'Внимание! Приближается дедлайн задачи!'")
                elif sys.platform.startswith("linux"):
                    os.system("espeak 'Attention! Task deadline approaching!'")
                elif sys.platform == "win32":
                    os.system("powershell -c \"[console]::beep(800,1000)\"")
        except Exception as e:
            print(f"Ошибка воспроизведения звука уведомления: {e}")
