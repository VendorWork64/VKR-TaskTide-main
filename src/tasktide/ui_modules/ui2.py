# ui2.py - Корпоративная версия

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMenu, QListWidgetItem, QMessageBox, QInputDialog, QDialog, QComboBox, QLineEdit, QSpinBox, QTextEdit, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import sqlite3
from datetime import datetime, timedelta
from src.tasktide.database import get_all_tasks, update_task_status, delete_task, update_task, add_completed_task_to_history
from src.tasktide.styles import get_button_style, get_default_style

class EditTaskDialog(QDialog):
    def clean_text_from_icons(self, text):
        """Удаляет иконки из текста"""
        icons = ['🔥', '⚠️', '📋', '📝', '⭐', '⚡', '💼', '📚', '👤', '🏠']
        for icon in icons:
            text = text.replace(icon, '').strip()
        return text
    
    def __init__(self, task, style):
        super().__init__()
        self.task = task
        self.setStyleSheet(style)
        self.setWindowTitle("Редактировать задачу")
        self.setFixedSize(400, 450)
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4f7fb, stop:1 #eef3f9);
                border-radius: 12px;
                border: 2px solid #d9e2ec;
            }
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #102a43;
                margin-bottom: 3px;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                font-size: 12px;
                background-color: #ffffff;
                margin-bottom: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                margin: 3px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок диалога
        title = QLabel("Редактировать задачу")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #102a43;
            margin-bottom: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Название задачи
        layout.addWidget(QLabel("Название задачи:"))
        self.name_input = QLineEdit(task[1])
        self.name_input.setMaxLength(20)
        layout.addWidget(self.name_input)
        
        # Приоритет
        layout.addWidget(QLabel("Приоритет:"))
        self.category1_combo = QComboBox()
        self.category1_combo.addItems([
            "Важно - Срочно",
            "Важно - Не срочно", 
            "Не важно - Срочно",
            "Не важно - Не срочно"
        ])
        # Очищаем приоритет от иконок перед установкой
        clean_priority = self.clean_text_from_icons(task[2])
        self.category1_combo.setCurrentText(clean_priority)
        layout.addWidget(self.category1_combo)
        
        # Категория
        layout.addWidget(QLabel("Категория:"))
        self.category2_combo = QComboBox()
        self.category2_combo.addItems(["Работа", "Учёба", "Личное"])
        # Очищаем категорию от иконок перед установкой
        clean_category = self.clean_text_from_icons(task[3])
        self.category2_combo.setCurrentText(clean_category)
        layout.addWidget(self.category2_combo)
        
        # Описание
        layout.addWidget(QLabel("Описание:"))
        self.description_input = QTextEdit(task[6] if task[6] else "")
        self.description_input.setMaximumHeight(70)
        layout.addWidget(self.description_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #1f7a57;
                color: white;
            }
        """)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #627d98;
                color: white;
            }
        """)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_changes(self):
        name = self.name_input.text()
        category1 = self.clean_text_from_icons(self.category1_combo.currentText())
        category2 = self.clean_text_from_icons(self.category2_combo.currentText())
        description = self.description_input.toPlainText()
        
        
        if not name.strip():
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым!")
            return
        
        # Сохраняем изменения в базе данных
        update_task(self.task[0], name, category1, category2, self.task[4], description)
        QMessageBox.information(self, "Успех", "Задача успешно обновлена!")
        self.accept()

class TaskListView(QWidget):
    def __init__(self, show_tasks_callback):
        super().__init__()
        self.show_tasks_callback = show_tasks_callback
        self.setWindowTitle("TaskTide - Список задач")
        self.resize(1000, 900)  # Устанавливаем начальный размер, но не фиксируем его
        self.current_filter = "Все приоритеты"

        # Базовый стиль приложения
        self.setStyleSheet(get_default_style())

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        # Корпоративная панель управления
        control_panel = QFrame()
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #f4f7fb;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 12px;
                margin-bottom: 8px;
            }
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setSpacing(12)  # Увеличиваем расстояние между элементами
        control_layout.setContentsMargins(15, 15, 15, 15)  # Добавляем отступы
        
        # Левая часть - кнопка назад
        back_button = QPushButton("← Назад")
        back_button.clicked.connect(show_tasks_callback)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #486581;
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: 600;
                min-width: 80px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #5a6268;
                border-color: #102a43;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        control_layout.addWidget(back_button)
        
        control_layout.addStretch()
        
        # Центральная часть - фильтры
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)  # Увеличиваем расстояние между фильтрами
        
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems([
            "Все приоритеты",
            "Важно - Срочно",
            "Важно - Не срочно", 
            "Не важно - Срочно",
            "Не важно - Не срочно"
        ])
        self.priority_filter.currentTextChanged.connect(self.filter_tasks)
        self.priority_filter.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 600;
                color: #102a43;
                min-width: 110px;
                margin: 2px 2px 2px 0px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: #f0f0f0;
                border-left: 2px solid #d9e2ec;
                border-radius: 0 4px 4px 0;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #627d98;
                width: 0;
                height: 0;
            }
            QComboBox::down-arrow:hover {
                border-top: 6px solid #666666;
            }
            QComboBox:hover {
                border-color: #102a43;
            }
            QComboBox:focus {
                border-color: #102a43;
                border-width: 3px;
            }
        """)
        filter_layout.addWidget(self.priority_filter)
        
        # Фильтр по статусу
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все статусы", "Не начата", "В процессе", "Выполнена", "Просрочены", "Не просрочены"])
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        self.status_filter.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 600;
                color: #102a43;
                min-width: 100px;
                margin: 2px 2px 2px 4px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: #f0f0f0;
                border-left: 2px solid #d9e2ec;
                border-radius: 0 4px 4px 0;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #627d98;
                width: 0;
                height: 0;
            }
            QComboBox::down-arrow:hover {
                border-top: 6px solid #666666;
            }
            QComboBox:hover {
                border-color: #102a43;
            }
            QComboBox:focus {
                border-color: #102a43;
                border-width: 3px;
            }
        """)
        filter_layout.addWidget(self.status_filter)
        
        # Фильтр по категориям
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Все категории", "Работа", "Учёба", "Личное"])
        self.category_filter.currentTextChanged.connect(self.filter_tasks)
        self.category_filter.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 600;
                color: #102a43;
                min-width: 107px;
                margin: 2px 2px 2px 0px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: #f0f0f0;
                border-left: 2px solid #d9e2ec;
                border-radius: 0 4px 4px 0;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #627d98;
                width: 0;
                height: 0;
            }
            QComboBox::down-arrow:hover {
                border-top: 6px solid #666666;
            }
            QComboBox:hover {
                border-color: #102a43;
            }
            QComboBox:focus {
                border-color: #102a43;
                border-width: 3px;
            }
        """)
        filter_layout.addWidget(self.category_filter)
        
        control_layout.addLayout(filter_layout)
        control_layout.addStretch()
        
        # Правая часть - кнопка обновления
        refresh_button = QPushButton("🔄 Обновить")
        refresh_button.clicked.connect(self.load_tasks)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #1f7a57;
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #176547;
                border-color: #102a43;
            }
            QPushButton:pressed {
                background-color: #0f5137;
            }
        """)
        control_layout.addWidget(refresh_button)
        
        self.layout.addWidget(control_panel)


        # Статистика в корпоративном стиле
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            font-size: 12px;
            color: #486581;
            padding: 8px 12px;
            background-color: #f4f7fb;
            border-radius: 4px;
            border: 2px solid #d9e2ec;
            margin-bottom: 8px;
        """)
        self.layout.addWidget(self.stats_label)

        # Корпоративный список задач
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.task_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)  # Плавная прокрутка
        self.task_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем горизонтальную прокрутку
        self.task_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем вертикальную прокрутку
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 0;
                margin: 0;
                height: 35px;
            }
        """)
        self.layout.addWidget(self.task_list)

        # Навигация по страницам
        self.current_page = 0
        self.tasks_per_page = 6
        
        # Создаем контейнер для навигации
        navigation_widget = QWidget()
        navigation_widget.setFixedHeight(40)  # Фиксированная высота для навигации
        navigation_layout = QHBoxLayout(navigation_widget)
        navigation_layout.setContentsMargins(10, 5, 10, 5)
        navigation_layout.setSpacing(10)
        
        # Кнопка "Назад"
        self.prev_button = QPushButton("←")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #486581;
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: 600;
                min-width: 15px;
                max-width: 15px;
            }
            QPushButton:hover {
                background-color: #5a6268;
                border-color: #102a43;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
            QPushButton:disabled {
                background-color: #eef3f9;
                color: #486581;
                border-color: #102a43;
            }
        """)
        self.prev_button.clicked.connect(self.prev_page)
        navigation_layout.addWidget(self.prev_button)
        
        # Информация о странице
        self.page_info = QLabel("Страница 1 из 1")
        self.page_info.setStyleSheet("""
            QLabel {
                color: #486581;
                font-size: 11px;
                font-weight: 500;
                padding: 5px 10px;
            }
        """)
        navigation_layout.addWidget(self.page_info)
        
        # Кнопка "Вперед"
        self.next_button = QPushButton("→")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #486581;
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: 600;
                min-width: 15px;
                max-width: 15px;
            }
            QPushButton:hover {
                background-color: #5a6268;
                border-color: #102a43;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
            QPushButton:disabled {
                background-color: #eef3f9;
                color: #486581;
                border-color: #102a43;
            }
        """)
        self.next_button.clicked.connect(self.next_page)
        navigation_layout.addWidget(self.next_button)
        
        # Добавляем навигацию в левый нижний угол
        self.layout.addWidget(navigation_widget, alignment=Qt.AlignBottom | Qt.AlignLeft)
        
        # Убеждаемся, что навигация видна
        navigation_widget.setVisible(True)
        navigation_widget.setStyleSheet("""
            QWidget {
                background-color: #f4f7fb;
                border: 2px solid #d9e2ec;
                border-radius: 4px;
            }
        """)
        print(f"Навигация создана: {navigation_widget.isVisible()}")
        print(f"Размер навигации: {navigation_widget.size()}")
        print(f"Позиция навигации: {navigation_widget.pos()}")

        self.load_tasks()

    def update_theme_styles(self, is_dark_theme=False):
        """Обновляет стили элементов в зависимости от темы"""
        if is_dark_theme:
            # Стили для тёмной темы
            self.task_list.setStyleSheet("""
                QListWidget {
                    background-color: #1a1a1a;
                    border: 2px solid #ffffff;
                    border-radius: 6px;
                    outline: none;
                    padding: 4px;
                }
                QListWidget::item {
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    margin: 0;
                    height: 35px;
                }
            """)
            
            # Обновляем стили панели управления
            control_panel = self.layout.itemAt(0).widget()
            if control_panel:
                control_panel.setStyleSheet("""
                    QFrame {
                        background-color: #2a2a2a;
                        border: 2px solid #ffffff;
                        border-radius: 6px;
                        padding: 12px;
                        margin-bottom: 8px;
                    }
                """)
            
            # Обновляем стили статистики
            self.stats_label.setStyleSheet("""
                font-size: 12px;
                color: #b8c5d1;
                padding: 8px 12px;
                background-color: #2a2a2a;
                border-radius: 4px;
                border: 2px solid #ffffff;
                margin-bottom: 8px;
            """)
            
            # Обновляем стили навигации
            navigation_widget = self.layout.itemAt(2).widget()  # Навигация обычно третий элемент
            if navigation_widget:
                navigation_widget.setStyleSheet("""
                    QWidget {
                        background-color: #2a2a2a;
                        border: 2px solid #ffffff;
                        border-radius: 4px;
                    }
                """)
        else:
            # Стили для светлой темы (возвращаем оригинальные)
            self.task_list.setStyleSheet("""
                QListWidget {
                    background-color: #ffffff;
                    border: 2px solid #d9e2ec;
                    border-radius: 6px;
                    outline: none;
                    padding: 4px;
                }
                QListWidget::item {
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    margin: 0;
                    height: 35px;
                }
            """)
            
            # Обновляем стили панели управления
            control_panel = self.layout.itemAt(0).widget()
            if control_panel:
                control_panel.setStyleSheet("""
                    QFrame {
                        background-color: #f4f7fb;
                        border: 2px solid #d9e2ec;
                        border-radius: 6px;
                        padding: 12px;
                        margin-bottom: 8px;
                    }
                """)
            
            # Обновляем стили статистики
            self.stats_label.setStyleSheet("""
                font-size: 12px;
                color: #486581;
                padding: 8px 12px;
                background-color: #f4f7fb;
                border-radius: 4px;
                border: 2px solid #d9e2ec;
                margin-bottom: 8px;
            """)
            
            # Обновляем стили навигации
            navigation_widget = self.layout.itemAt(2).widget()  # Навигация обычно третий элемент
            if navigation_widget:
                navigation_widget.setStyleSheet("""
                    QWidget {
                        background-color: #f4f7fb;
                        border: 2px solid #d9e2ec;
                        border-radius: 4px;
                    }
                """)

    def filter_tasks(self, selected_filter):
        """Фильтрует задачи по выбранному приоритету и статусу."""
        print(f"Фильтр изменён: {selected_filter}")
        print(f"Приоритет: {self.priority_filter.currentText()}")
        print(f"Статус: {self.status_filter.currentText()}")
        self.current_page = 0  # Сбрасываем на первую страницу при фильтрации
        self.load_tasks()
    
    def prev_page(self):
        """Переход на предыдущую страницу."""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_tasks()
    
    def next_page(self):
        """Переход на следующую страницу."""
        all_tasks = get_all_tasks()
        filtered_tasks = self.get_filtered_tasks(all_tasks)
        total_pages = (len(filtered_tasks) + self.tasks_per_page - 1) // self.tasks_per_page
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_tasks()
    
    def get_filtered_tasks(self, all_tasks):
        """Получает отфильтрованные задачи."""
        filtered_tasks = []
        priority_filter = self.priority_filter.currentText()
        status_filter = self.status_filter.currentText()
        category_filter = self.category_filter.currentText()
        
        print(f"Фильтрация: приоритет='{priority_filter}', статус='{status_filter}', категория='{category_filter}'")
        print(f"Всего задач: {len(all_tasks)}")
        
        for task in all_tasks:
            # Фильтр по приоритету
            priority_match = True
            if priority_filter != "Все приоритеты":
                # Убираем иконки из приоритета задачи для сравнения
                task_priority = task[2]
                # Удаляем возможные иконки
                for icon in ['🔥', '⚠️', '📋', '📝', '⭐', '⚡']:
                    task_priority = task_priority.replace(icon, '').strip()
                
                priority_match = task_priority == priority_filter
                print(f"Задача '{task[1]}': приоритет '{task[2]}' -> '{task_priority}' == '{priority_filter}' -> {priority_match}")
            
            # Фильтр по статусу
            status_match = True
            if status_filter != "Все статусы":
                task_status = task[5].lower()
                filter_status = status_filter.lower()
                
                # Проверяем просроченность задачи
                is_overdue = False
                try:
                    deadline = datetime.fromisoformat(task[4])
                    now = datetime.now()
                    is_overdue = deadline < now
                except:
                    is_overdue = False
                
                # Маппинг для фильтрации
                status_filter_mapping = {
                    'не начата': ['не начата', 'not started'],
                    'в процессе': ['в процессе', 'in progress'],
                    'выполнена': ['выполнена', 'completed']
                }
                
                status_match = False
                
                # Специальная обработка для просроченных задач
                if filter_status == 'просрочены':
                    status_match = is_overdue
                elif filter_status == 'не просрочены':
                    status_match = not is_overdue
                else:
                    # Обычная фильтрация по статусу
                    for key, values in status_filter_mapping.items():
                        if filter_status == key:
                            status_match = task_status in values
                            break
                
                print(f"Задача '{task[1]}': статус '{task_status}', просрочена: {is_overdue} -> {status_match}")
            
            # Фильтр по категории
            category_match = True
            if category_filter != "Все категории":
                task_category = task[3]
                # Очищаем категорию от иконок для сравнения
                clean_category = task_category
                for icon in ['💼', '📚', '👤', '🏠']:
                    clean_category = clean_category.replace(icon, '').strip()
                
                category_match = clean_category == category_filter
                print(f"Задача '{task[1]}': категория '{task_category}' -> '{clean_category}' == '{category_filter}' -> {category_match}")
            
            if priority_match and status_match and category_match:
                filtered_tasks.append(task)
                print(f"Задача '{task[1]}' прошла фильтр")
        
        # Сортируем задачи по оставшемуся времени (сначала самые срочные)
        def get_sort_key(task):
            try:
                deadline = datetime.fromisoformat(task[4])
                now = datetime.now()
                
                if deadline < now:
                    return (0, deadline)  # Просроченные задачи идут первыми
                else:
                    return (1, deadline)  # Затем по времени до дедлайна
            except:
                return (2, datetime.max)  # Задачи без дедлайна идут последними
        
        filtered_tasks.sort(key=get_sort_key)
        return filtered_tasks

    def get_time_remaining(self, deadline_str):
        """Возвращает оставшееся время до дедлайна."""
        try:
            deadline = datetime.fromisoformat(deadline_str)
            now = datetime.now()
            
            if deadline < now:
                return "Просрочено"
            
            delta = deadline - now
            
            if delta.days > 0:
                return f"{delta.days}д"
            elif delta.seconds // 3600 > 0:
                return f"{delta.seconds // 3600}ч"
            else:
                return f"{delta.seconds // 60}м"
                
        except:
            return "—"

    def load_tasks(self):
        """Загружает задачи из базы данных и отображает их в списке."""
        self.task_list.clear()
        all_tasks = get_all_tasks()
        
        # Получаем отфильтрованные задачи
        filtered_tasks = self.get_filtered_tasks(all_tasks)
        
        # Вычисляем пагинацию
        total_pages = (len(filtered_tasks) + self.tasks_per_page - 1) // self.tasks_per_page
        start_index = self.current_page * self.tasks_per_page
        end_index = min(start_index + self.tasks_per_page, len(filtered_tasks))
        page_tasks = filtered_tasks[start_index:end_index]
        
        # Обновляем кнопки навигации
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        
        # Обновляем информацию о странице
        if total_pages > 0:
            self.page_info.setText(f"Страница {self.current_page + 1} из {total_pages}")
        else:
            self.page_info.setText("Страница 1 из 1")
        
        # Обновляем статистику
        total_tasks = len(all_tasks)
        filtered_count = len(filtered_tasks)
        self.stats_label.setText(f"Задач: {filtered_count}/{total_tasks} | Фильтр: {self.priority_filter.currentText()} | {self.status_filter.currentText()} | {self.category_filter.currentText()}")

        if not page_tasks:
            if len(filtered_tasks) == 0:
                empty_message = "Задачи не найдены. Измените фильтры или создайте новую задачу."
            else:
                empty_message = "На этой странице нет задач."
            empty_item = QListWidgetItem(empty_message)
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFont(QFont("Segoe UI", 12))
            self.task_list.addItem(empty_item)
            return

        # Сортируем ВСЕ задачи по срочности (независимо от статуса)
        def get_sort_key(task):
            try:
                deadline = datetime.fromisoformat(task[4])
                now = datetime.now()
                
                if deadline < now:
                    return (0, deadline)  # Просроченные задачи идут первыми
                else:
                    return (1, deadline)  # Затем по времени до дедлайна
            except:
                return (2, datetime.max)  # Задачи без дедлайна идут последними
        
        page_tasks.sort(key=get_sort_key)
        
        # Отображаем задачи в отсортированном порядке без группировки
        for task in page_tasks:
            self.add_task_item(task)

    def add_task_item(self, task):
        """Добавляет одну задачу в список."""
        task_widget = QFrame()
        
        # Определяем, какая тема активна (проверяем стиль основного виджета)
        is_dark_theme = "#00202e" in self.styleSheet()
        
        if is_dark_theme:
            # Стили для тёмной темы
            task_widget.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2a;
                    border: 1px solid #ffffff;
                    border-bottom: 2px solid #ffffff;
                    border-radius: 6px;
                    padding: 0;
                    margin: 1px 0;
                    min-height: 35px;
                    max-height: 35px;
                }
                QFrame:hover {
                    border-color: #1f7a57;
                    border-bottom: 2px solid #ffffff;
                    background-color: #3a3a3a;
                }
            """)
        else:
            # Стили для светлой темы
            task_widget.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e1e5e9;
                    border-bottom: 2px solid #d9e2ec;
                    border-radius: 6px;
                    padding: 0;
                    margin: 1px 0;
                    min-height: 35px;
                    max-height: 35px;
                }
                QFrame:hover {
                    border-color: #1f7a57;
                    border-bottom: 2px solid #d9e2ec;
                    background-color: #f4f7fb;
                }
            """)
        
        # Добавляем всплывающую подсказку с описанием задачи
        description = task[3] if len(task) > 3 and task[3] else "Описание не указано"
        task_widget.setToolTip(f"Описание: {description}")
        
        # Создаем один общий контейнер без отступов
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignLeft)  # Выравниваем по левому краю
        
        # Создаем один общий виджет для всех колонок
        content_widget = QWidget()
        content_widget.setFixedWidth(731)  # Общая ширина всех колонок
        content_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Создаем внутренний макет без отступов
        inner_layout = QHBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)
        inner_layout.setAlignment(Qt.AlignLeft)  # Выравниваем по левому краю
        
        # Колонка 1: Приоритет - 150px
        priority_colors = {
            'Важно - Срочно': {'color': '#cf3f2f', 'bg': '#f8d7da'},
            'Важно - Не срочно': {'color': '#fd7e14', 'bg': '#fff3cd'},
            'Не важно - Срочно': {'color': '#0d6efd', 'bg': '#cff4fc'},
            'Не важно - Не срочно': {'color': '#486581', 'bg': '#f4f7fb'}
        }
        
        # Очищаем приоритет от иконок для получения правильного цвета
        priority_text = task[2]
        clean_priority = priority_text
        for icon in ['🔥', '⚠️', '📋', '📝', '⭐', '⚡']:
            clean_priority = clean_priority.replace(icon, '').strip()
        
        # Получаем информацию о цвете для очищенного приоритета
        priority_info = priority_colors.get(clean_priority, {'color': '#486581', 'bg': '#f4f7fb'})
        
        # Показываем только текст без иконок для всех приоритетов
        priority_text = clean_priority
        
        priority_label = QLabel(priority_text)
        
        # Адаптивные стили для приоритета
        if is_dark_theme:
            priority_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {priority_info['bg']};
                    color: {priority_info['color']};
                    border: 1px solid #ffffff;
                    border-bottom: 2px solid #ffffff;
                    margin: 0px;
                    padding: 0px;
                    font-size: 13px;
                    font-weight: 600;
                }}
            """)
        else:
            priority_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {priority_info['bg']};
                    color: {priority_info['color']};
                    border: 1px solid #d9e2ec;
                    border-bottom: 2px solid #d9e2ec;
                    margin: 0px;
                    padding: 0px;
                    font-size: 13px;
                    font-weight: 600;
                }}
            """)
        priority_label.setAlignment(Qt.AlignCenter)
        priority_label.setFixedWidth(150)
        priority_label.mouseDoubleClickEvent = lambda event: self.edit_task_priority(task)
        inner_layout.addWidget(priority_label)
        
        # Колонка 2: Категория - 80px
        # Добавляем иконку к категории в зависимости от типа (только если её нет)
        category_text = task[3]
        
        # Проверяем точное совпадение категории и отсутствие иконки
        if category_text == 'Работа' and '💼' not in category_text:
            category_text = f"💼 {category_text}"
        elif category_text == 'Учёба' and '📚' not in category_text:
            category_text = f"📚 {category_text}"
        elif category_text == 'Личное' and '👤' not in category_text:
            category_text = f"👤 {category_text}"
        
        category_label = QLabel(category_text)
        
        # Адаптивные стили для категории
        if is_dark_theme:
            category_label.setStyleSheet("""
                QLabel {
                    color: #b8c5d1;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: #2a2a2a;
                    border: 1px solid #ffffff;
                    border-bottom: 2px solid #ffffff;
                    margin: 0px;
                    padding: 0px;
                }
            """)
        else:
            category_label.setStyleSheet("""
                QLabel {
                    color: #486581;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: #f4f7fb;
                    border: 1px solid #d9e2ec;
                    border-bottom: 2px solid #d9e2ec;
                    margin: 0px;
                    padding: 0px;
                }
            """)
        category_label.setAlignment(Qt.AlignCenter)
        category_label.setFixedWidth(80)
        category_label.mouseDoubleClickEvent = lambda event: self.edit_task_category(task)
        inner_layout.addWidget(category_label)
        
        # Колонка 3: Название задачи - 320px (увеличенный)
        # Обрезаем длинные названия для лучшего отображения
        task_title = task[1]
        if len(task_title) > 25:  # Если название длиннее 25 символов
            task_title = task_title[:22] + "..."  # Обрезаем и добавляем многоточие
        
        task_name = QLabel(task_title)
        
        # Добавляем всплывающую подсказку с полным названием
        if len(task[1]) > 25:
            task_name.setToolTip(f"Полное название: {task[1]}")
        
        # Адаптивные стили для названия задачи
        if is_dark_theme:
            task_name.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #ffffff;
                    background-color: #1a1a1a;
                    border: 1px solid #ffffff;
                    border-bottom: 2px solid #ffffff;
                    margin: 0px;
                    padding: 0px;
                }
            """)
        else:
            task_name.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #212529;
                    background-color: #ffffff;
                    border: 1px solid #d9e2ec;
                    border-bottom: 2px solid #d9e2ec;
                    margin: 0px;
                    padding: 0px;
                }
            """)
        task_name.setWordWrap(True)
        task_name.setAlignment(Qt.AlignCenter)
        task_name.setFixedWidth(310)  # 150 + 80 + 310 + 181 = 721px
        task_name.mouseDoubleClickEvent = lambda event: self.edit_task_name(task)
        inner_layout.addWidget(task_name)
        
        # Колонка 4: Оставшееся время - 170px (уменьшенный)
        time_remaining = self.get_time_remaining(task[4])
        time_label = QLabel(time_remaining)
        
        # Адаптивные стили для времени
        if is_dark_theme:
            time_label.setStyleSheet("""
                QLabel {
                    color: #b8c5d1;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: #2a2a2a;
                    border: 1px solid #ffffff;
                    border-bottom: 2px solid #ffffff;
                    margin: 0px;
                    padding: 0px;
                }
            """)
        else:
            time_label.setStyleSheet("""
                QLabel {
                    color: #486581;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: #f4f7fb;
                    border: 1px solid #d9e2ec;
                    border-bottom: 2px solid #d9e2ec;
                    margin: 0px;
                    padding: 0px;
                }
            """)
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setFixedWidth(187)  # 150 + 80 + 310 + 191 = 731px
        time_label.mouseDoubleClickEvent = lambda event: self.edit_task_deadline(task)
        inner_layout.addWidget(time_label)
        
        content_widget.setLayout(inner_layout)
        main_layout.addWidget(content_widget)
        
        # Всплывающее описание при наведении
        if len(task) > 6 and task[6] and task[6].strip():
            task_widget.setToolTip(f"Описание: {task[6]}")
        
        task_widget.setLayout(main_layout)
        
        # Создаем элемент списка
        task_item = QListWidgetItem()
        task_item.setData(Qt.UserRole, task)
        task_item.setSizeHint(task_widget.sizeHint())
        
        self.task_list.addItem(task_item)
        self.task_list.setItemWidget(task_item, task_widget)

    def change_task_status(self, item, new_status):
        """Изменяет статус задачи."""
        task = item.data(Qt.UserRole)
        update_task_status(task[0], new_status)
        
        if new_status == 'выполнена':
            add_completed_task_to_history()
            QMessageBox.information(self, "Поздравляем!", f"Задача '{task[1]}' выполнена! 🎉")
        
        self.load_tasks()

    def delete_task(self, item):
        """Удаляет задачу из базы данных."""
        task = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Подтверждение", 
                                   f"Вы уверены, что хотите удалить задачу '{task[1]}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            delete_task(task[0])
            self.load_tasks()

    def edit_task(self, item):
        """Редактирует задачу."""
        task = item.data(Qt.UserRole)
        
        dialog = EditTaskDialog(task, self.styleSheet())
        if dialog.exec_() == QDialog.Accepted:
            self.load_tasks()

    def show_context_menu(self, pos):
        """Показывает контекстное меню для управления задачами."""
        item = self.task_list.itemAt(pos)
        if item is None or not item.data(Qt.UserRole):
            return

        task = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
                font-size: 12px;
                border: 1px solid transparent;
            }
            QMenu::item:selected {
                background-color: #1f7a57;
                color: white;
                border: 1px solid #d9e2ec;
            }
        """)
        
        current_status = task[5]
        
        # Опции изменения статуса
        if current_status != 'выполнена':
            mark_done_action = menu.addAction("Отметить как выполненную")
        if current_status != 'в процессе':
            mark_progress_action = menu.addAction("Отметить как в процессе")
        if current_status != 'не начата':
            mark_not_started_action = menu.addAction("Отметить как не начатую")
        
        menu.addSeparator()
        edit_description_action = menu.addAction("Редактировать описание")
        delete_action = menu.addAction("Удалить задачу")

        action = menu.exec_(self.task_list.mapToGlobal(pos))

        if action == mark_done_action if current_status != 'выполнена' else None:
            self.change_task_status(item, 'выполнена')
        elif action == mark_progress_action if current_status != 'в процессе' else None:
            self.change_task_status(item, 'в процессе')
        elif action == mark_not_started_action if current_status != 'не начата' else None:
            self.change_task_status(item, 'не начата')
        elif action == edit_description_action:
            self.edit_task_description(item)
        elif action == delete_action:
            self.delete_task(item)
    
    def on_item_double_clicked(self, item):
        """Обработчик двойного клика по элементу списка."""
        self.edit_task(item)
    
    def edit_task_priority(self, task):
        """Редактирование приоритета задачи."""
        from PyQt5.QtWidgets import QInputDialog
        
        priorities = ['Важно - Срочно', 'Важно - Не срочно', 'Не важно - Срочно', 'Не важно - Не срочно']
        current_priority = task[2]
        
        # Очищаем текущий приоритет от иконок
        clean_priority = current_priority
        for icon in ['🔥', '⚠️', '📋', '📝', '⭐', '⚡']:
            clean_priority = clean_priority.replace(icon, '').strip()
        
        priority, ok = QInputDialog.getItem(self, 'Редактировать приоритет', 'Выберите приоритет:', priorities, priorities.index(clean_priority) if clean_priority in priorities else 0)
        
        if ok and priority != clean_priority:
            # Обновляем приоритет в базе данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET category1 = ? WHERE id = ?", (priority, task[0]))
            conn.commit()
            conn.close()
            
            # Обновляем список задач
            self.load_tasks()
    
    def edit_task_category(self, task):
        """Редактирование категории задачи."""
        from PyQt5.QtWidgets import QInputDialog
        
        categories = ['Работа', 'Учёба', 'Личное']
        current_category = task[3]
        
        # Очищаем текущую категорию от иконок
        clean_category = current_category
        for icon in ['💼', '📚', '👤', '🏠']:
            clean_category = clean_category.replace(icon, '').strip()
        
        category, ok = QInputDialog.getItem(self, 'Редактировать категорию', 'Выберите категорию:', categories, categories.index(clean_category) if clean_category in categories else 0)
        
        if ok and category != clean_category:
            # Обновляем категорию в базе данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET category2 = ? WHERE id = ?", (category, task[0]))
            conn.commit()
            conn.close()
            
            # Обновляем список задач
            self.load_tasks()
    
    def edit_task_name(self, task):
        """Редактирование названия задачи."""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, 'Редактировать название', 'Введите новое название:', text=task[1])
        
        if ok and name.strip() and name != task[1]:
            # Обновляем название в базе данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET name = ? WHERE id = ?", (name.strip(), task[0]))
            conn.commit()
            conn.close()
            
            # Обновляем список задач
            self.load_tasks()
    
    def edit_task_deadline(self, task):
        """Редактирование дедлайна задачи."""
        from PyQt5.QtWidgets import QInputDialog
        from datetime import datetime
        
        # Получаем текущий дедлайн
        current_deadline = task[4]
        
        # Парсим текущую дату
        try:
            if current_deadline:
                current_date = datetime.strptime(current_deadline, '%Y-%m-%d %H:%M')
                date_str = current_date.strftime('%Y-%m-%d')
                time_str = current_date.strftime('%H:%M')
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
                time_str = '12:00'
        except:
            date_str = datetime.now().strftime('%Y-%m-%d')
            time_str = '12:00'
        
        # Запрашиваем новую дату
        new_date, ok1 = QInputDialog.getText(self, 'Редактировать дату и время', 'Введите дату (YYYY-MM-DD):', text=date_str)
        
        if ok1 and new_date.strip():
            # Запрашиваем новое время
            new_time, ok2 = QInputDialog.getText(self, 'Редактировать дату и время', 'Введите время (HH:MM):', text=time_str)
            
            if ok2 and new_time.strip():
                try:
                    # Формируем новую дату и время
                    new_deadline = f"{new_date.strip()} {new_time.strip()}"
                    datetime.strptime(new_deadline, '%Y-%m-%d %H:%M')  # Проверяем корректность
                    
                    # Обновляем дедлайн в базе данных
                    conn = sqlite3.connect('tasks.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tasks SET deadline = ? WHERE id = ?", (new_deadline, task[0]))
                    conn.commit()
                    conn.close()
                    
                    # Обновляем список задач
                    self.load_tasks()
                except ValueError:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, 'Ошибка', 'Неверный формат даты или времени!')
    
    def edit_task_description(self, item):
        """Редактирование описания задачи."""
        from PyQt5.QtWidgets import QInputDialog
        
        # Получаем данные задачи из item
        task_data = item.data(Qt.UserRole)
        if not task_data:
            return
        
        # Получаем текущее описание
        current_description = task_data[3] if len(task_data) > 3 and task_data[3] else ""
        
        # Запрашиваем новое описание
        new_description, ok = QInputDialog.getText(self, 'Редактировать описание', 'Введите описание задачи:', text=current_description)
        
        if ok and new_description.strip() != current_description:
            # Обновляем описание в базе данных
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET description = ? WHERE id = ?", (new_description.strip(), task_data[0]))
            conn.commit()
            conn.close()
            
            # Обновляем список задач
            self.load_tasks()
