# ui3.py - Модуль заметок для задач

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, 
    QMenu, QListWidgetItem, QMessageBox, QInputDialog, QDialog, QComboBox, 
    QLineEdit, QTextEdit, QFrame, QSplitter, QScrollArea, QGroupBox,
    QCheckBox, QDateEdit, QTimeEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QSize, QDateTime, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
import sqlite3
from datetime import datetime, timedelta
from src.tasktide.database import get_all_tasks
from src.tasktide.notes_db import add_note, get_all_notes, get_note_by_id, update_note, delete_note, search_notes, pin_note, get_notes_by_task, get_notes_by_parent, get_note_hierarchy
from src.tasktide.styles import get_button_style, get_default_style

class TaskSelectorDialog(QDialog):
    """Диалог выбора задачи"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите задачу")
        self.setFixedSize(600, 500)
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4f7fb, stop:1 #eef3f9);
                border-radius: 12px;
                border: 2px solid #d9e2ec;
            }
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #102a43;
                margin-bottom: 8px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                font-size: 14px;
                background-color: #ffffff;
                margin-bottom: 10px;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                background-color: #ffffff;
                border: 1px solid #eef3f9;
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
                min-height: 50px;
                color: #102a43;
            }
            QListWidget::item:selected {
                background-color: #e6f4ea;
                border: 2px solid #1f7a57;
                color: #102a43;
            }
            QListWidget::item:hover {
                background-color: #f4f7fb;
                border: 1px solid #1f7a57;
                color: #102a43;
            }
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                margin: 5px;
            }
        """)
        
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel("📋 Выберите задачу для работы с подзадачами")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #102a43;
            margin-bottom: 15px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Поиск
        search_label = QLabel("🔍 Поиск по названию задачи:")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название задачи...")
        self.search_input.textChanged.connect(self.filter_tasks)
        layout.addWidget(self.search_input)
        
        # Список задач
        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.tasks_list)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ Выбрать")
        select_btn.clicked.connect(self.accept)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
            }
        """)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #cf3f2f;
                color: white;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_tasks(self):
        """Загружает все задачи"""
        self.tasks_list.clear()
        
        try:
            tasks = get_all_tasks()
            
            if not tasks:
                item = QListWidgetItem("📝 Задач пока нет")
                item.setTextAlignment(Qt.AlignCenter)
                self.tasks_list.addItem(item)
                return
            
            for task in tasks:
                item = QListWidgetItem()
                
                # Формируем текст для отображения
                task_name = task[1]  # название
                task_status = task[5]  # статус
                task_priority = task[2]  # приоритет
                task_category = task[3]  # категория
                
                # Иконки для статуса
                status_icons = {
                    'не начата': '⏳',
                    'в процессе': '🔄', 
                    'выполнена': '✅'
                }
                
                status_icon = status_icons.get(task_status, '📋')
                
                item_text = f"{status_icon} {task_name}\n{task_priority} • {task_category} • {task_status}"
                
                item.setText(item_text)
                item.setData(Qt.UserRole, task)
                
                # Цветовое кодирование по статусу
                if task_status == 'выполнена':
                    item.setBackground(QColor("#d4edda"))
                elif task_status == 'в процессе':
                    item.setBackground(QColor("#fff3cd"))
                
                self.tasks_list.addItem(item)
                
        except Exception as e:
            item = QListWidgetItem("❌ Ошибка загрузки задач")
            item.setTextAlignment(Qt.AlignCenter)
            self.tasks_list.addItem(item)
    
    def filter_tasks(self):
        """Фильтрует задачи по поиску"""
        search_text = self.search_input.text().strip().lower()
        
        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            if not item.data(Qt.UserRole):
                continue
                
            task = item.data(Qt.UserRole)
            task_name = task[1].lower()
            
            if search_text in task_name:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def get_selected_task(self):
        """Возвращает выбранную задачу"""
        current_item = self.tasks_list.currentItem()
        if current_item and current_item.data(Qt.UserRole):
            return current_item.data(Qt.UserRole)
        return None

class NoteEditor(QDialog):
    """Редактор заметок"""
    
    def __init__(self, task, parent_note_id=None, note_data=None, parent=None):
        super().__init__(parent)
        self.task = task
        self.parent_note_id = parent_note_id
        self.note_data = note_data
        # Обрезаем длинное название задачи для заголовка
        task_title = task[1]
        if len(task_title) > 30:
            task_title = task_title[:27] + "..."
        
        if parent_note_id:
            self.setWindowTitle(f"Создать подзадачу 2-го уровня для: {task_title}")
        else:
            self.setWindowTitle(f"Заметка для задачи: {task_title}")
        self.setFixedSize(500, 400)
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4f7fb, stop:1 #eef3f9);
                border-radius: 12px;
                border: 2px solid #d9e2ec;
            }
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #102a43;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                font-size: 14px;
                background-color: #ffffff;
                margin-bottom: 10px;
            }
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #d9e2ec;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                margin: 5px;
            }
        """)
        
        self.setup_ui()
        if note_data:
            self.load_note_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок - обрезаем длинное название
        task_title = self.task[1]
        if len(task_title) > 25:
            task_title = task_title[:22] + "..."
        
        if self.parent_note_id:
            title_label = QLabel(f"📝 Создать подзадачу n-го уровня для: {task_title}")
        else:
            title_label = QLabel(f"📝 Заметка для задачи: {task_title}")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #102a43;
            margin-bottom: 15px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Название заметки
        layout.addWidget(QLabel("Название заметки:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название заметки...")
        layout.addWidget(self.title_input)
        
        # Содержимое заметки
        layout.addWidget(QLabel("Содержимое заметки:"))
        self.content_editor = QTextEdit()
        self.content_editor.setMinimumHeight(150)
        self.content_editor.setPlaceholderText("Введите текст заметки...")
        layout.addWidget(self.content_editor)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.save_note)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
            }
        """)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #cf3f2f;
                color: white;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_note_data(self):
        """Загружает данные существующей заметки"""
        if self.note_data:
            self.title_input.setText(self.note_data[1])
            self.content_editor.setPlainText(self.note_data[2])
    
    def save_note(self):
        """Сохраняет заметку"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название заметки не может быть пустым!")
            return
        
        content = self.content_editor.toPlainText()
        
        try:
            if self.note_data:
                # Обновляем существующую заметку
                update_note(self.note_data[0], title, content, "📝 Общие заметки", "")
            else:
                # Создаем новую заметку или подзадачу
                print(f"Создаем заметку: title={title}, content={content}, task_id={self.task[0]}, parent_note_id={self.parent_note_id}")
                add_note(title, content, "📝 Общие заметки", self.task[0], "", self.parent_note_id)
            
            QMessageBox.information(self, "Успех", "Заметка сохранена!")
            self.accept()
        except Exception as e:
            print(f"Ошибка при сохранении заметки: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить заметку: {str(e)}")

class NotesView(QWidget):
    """Главное окно заметок"""
    
    def __init__(self, show_notes_callback):
        super().__init__()
        self.show_notes_callback = show_notes_callback
        self.current_task = None
        self.current_parent_note = None  # Текущая родительская заметка для навигации
        self.navigation_stack = []  # Стек навигации для возврата назад
        self.setWindowTitle("TaskTide - Заметки")
        self.resize(1000, 700)
        
        # Стиль заметок
        self.setStyleSheet(get_default_style() + """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4f7fb, stop:1 #eef3f9);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                outline: none;
                padding: 8px;
            }
            QListWidget::item {
                background-color: #ffffff;
                border: 1px solid #eef3f9;
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
                min-height: 60px;
                color: #102a43;
            }
            QListWidget::item:selected {
                background-color: #e6f4ea;
                border: 2px solid #1f7a57;
                color: #102a43;
            }
            QListWidget::item:hover {
                background-color: #f4f7fb;
                border: 1px solid #1f7a57;
                color: #102a43;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.5;
                color: #102a43;
            }
            QTextEdit[theme="dark"] {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса заметок"""
        
        # Кнопка назад
        back_button = QPushButton("← Назад")
        back_button.clicked.connect(self.show_notes_callback)
        back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #486581, stop:1 #5a6268);
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6268, stop:1 #495057);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #495057, stop:1 #343a40);
            }
        """)
        self.layout.addWidget(back_button)
        
        # Кнопка выбора задачи
        self.task_button = QPushButton("📋 Выберите задачу")
        self.task_button.clicked.connect(self.select_task)
        self.task_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f7a57, stop:1 #176547);
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
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
        self.layout.addWidget(self.task_button)
        
        # Панель навигации (хлебные крошки)
        self.navigation_frame = QFrame()
        self.navigation_frame.setFrameStyle(QFrame.Box)
        self.navigation_frame.setMaximumHeight(50)
        self.navigation_frame.hide()  # Скрываем по умолчанию
        
        navigation_layout = QHBoxLayout(self.navigation_frame)
        navigation_layout.setContentsMargins(10, 5, 10, 5)
        
        self.navigation_label = QLabel("")
        self.navigation_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #486581;
                background-color: #f4f7fb;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px 10px;
            }
        """)
        navigation_layout.addWidget(self.navigation_label)
        
        self.back_to_parent_btn = QPushButton("← Назад к родителю")
        self.back_to_parent_btn.clicked.connect(self.go_back_to_parent)
        self.back_to_parent_btn.setStyleSheet("""
            QPushButton {
                background-color: #486581;
                color: white;
                border: 1px solid #d9e2ec;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        navigation_layout.addWidget(self.back_to_parent_btn)
        
        self.layout.addWidget(self.navigation_frame)
        
        # Кнопка добавления заметки
        self.add_note_button = QPushButton("➕ Добавить подзаметку")
        self.add_note_button.clicked.connect(self.add_note)
        self.add_note_button.setEnabled(False)
        self.add_note_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #218838);
                color: white;
                border: 2px solid #d9e2ec;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: 600;
                min-width: 140px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #218838, stop:1 #1e7e34);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e7e34, stop:1 #1c7430);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
                border-color: #999999;
            }
        """)
        self.layout.addWidget(self.add_note_button)
        
        # Основная область
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Список заметок
        self.notes_list = QListWidget()
        self.notes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)
        self.notes_list.itemDoubleClicked.connect(self.on_note_double_clicked)
        self.notes_list.itemClicked.connect(self.on_note_selected)
        
        # Область просмотра заметки
        self.note_viewer = QTextEdit()
        self.note_viewer.setReadOnly(True)
        self.note_viewer.setPlaceholderText("Выберите заметку для просмотра...")
        
        main_splitter.addWidget(self.notes_list)
        main_splitter.addWidget(self.note_viewer)
        main_splitter.setSizes([400, 600])
        
        self.layout.addWidget(main_splitter)
    
    def select_task(self):
        """Выбор задачи"""
        dialog = TaskSelectorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_task = dialog.get_selected_task()
            if self.current_task:
                # Обрезаем длинное название задачи для кнопки
                task_title = self.current_task[1]
                if len(task_title) > 20:
                    task_title = task_title[:17] + "..."
                self.task_button.setText(f"📋 {task_title}")
                self.add_note_button.setEnabled(True)
                self.load_notes()
    
    def load_notes(self):
        """Загружает заметки для выбранной задачи или подзадачи"""
        self.notes_list.clear()
        
        if not self.current_task:
            item = QListWidgetItem("📝 Выберите задачу для просмотра заметок")
            item.setTextAlignment(Qt.AlignCenter)
            self.notes_list.addItem(item)
            return
        
        try:
            if self.current_parent_note:
                # Загружаем подзадачи n-го уровня
                notes = get_notes_by_parent(self.current_parent_note[0])
                empty_message = "📝 У этой подзадачи пока нет подзадач n-го уровня"
            else:
                # Загружаем обычные подзадачи
                notes = get_notes_by_task(self.current_task[0])
                empty_message = "📝 У этой задачи пока нет подзадач"
            
            if not notes:
                item = QListWidgetItem(empty_message)
                item.setTextAlignment(Qt.AlignCenter)
                self.notes_list.addItem(item)
                return
            
            for note in notes:
                item = QListWidgetItem()
                
                title = note[2]  # title (индекс 2)
                content = note[3]  # content (индекс 3)
                created_at = note[7]  # created_at (индекс 7)
                
                # Обрезаем содержимое для предварительного просмотра
                preview = content[:100] + "..." if len(content) > 100 else content
                
                item_text = f"📌 {title}\n{preview}\n📅 {created_at}"
                
                item.setText(item_text)
                item.setData(Qt.UserRole, note)
                
                self.notes_list.addItem(item)
                
        except Exception as e:
            item = QListWidgetItem("❌ Ошибка загрузки заметок")
            item.setTextAlignment(Qt.AlignCenter)
            self.notes_list.addItem(item)
    
    def add_note(self):
        """Добавляет новую заметку или подзадачу"""
        if not self.current_task:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите задачу!")
            return
        
        # Определяем, создаем ли мы подзадачу n-го уровня
        parent_note_id = None
        if self.current_parent_note:
            parent_note_id = self.current_parent_note[0]
        
        dialog = NoteEditor(self.current_task, parent_note_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_notes()
    
    def on_note_selected(self, item):
        """Показывает заметку при выборе"""
        note_data = item.data(Qt.UserRole)
        if not note_data:
            return
        
        print(f"Выбрана заметка: {note_data}")
        
        # Показываем заметку в области просмотра
        title = note_data[2]  # title (индекс 2)
        content = note_data[3]  # content (индекс 3)
        created_at = note_data[7]  # created_at (индекс 7)
        
        print(f"Title: {title}, Content: {content}, Created: {created_at}")
        
        html_content = f"""
        <div style='color: #102a43; background-color: #ffffff; font-family: Arial, sans-serif;'>
            <h2 style='color: #102a43; margin: 0 0 10px 0; font-size: 18px; font-weight: bold;'>📌 {title}</h2>
            <p style='color: #333333; margin: 0 0 15px 0; font-size: 14px;'><strong>Создано:</strong> {created_at}</p>
            <hr style='border: 1px solid #cccccc; margin: 15px 0;'>
            <div style='background: #f4f7fb; padding: 15px; border-radius: 8px; margin: 10px 0; color: #102a43; font-size: 14px; line-height: 1.5;'>
                {content.replace(chr(10), '<br>')}
            </div>
        </div>
        """
        
        self.note_viewer.setHtml(html_content)
    
    def edit_note(self, item):
        """Редактирует заметку"""
        note_data = item.data(Qt.UserRole)
        if not note_data:
            return
        
        # Для редактирования заметки нужно передать task и note_data
        dialog = NoteEditor(self.current_task, note_data=note_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_notes()
    
    def on_note_double_clicked(self, item):
        """Обрабатывает двойной клик по заметке - открывает подзадачи n-го уровня"""
        note_data = item.data(Qt.UserRole)
        if not note_data:
            return
        
        # Проверяем, есть ли подзадачи у этой заметки
        note_id = note_data[0]
        subtasks = get_notes_by_parent(note_id)
        
        if subtasks:
            # Есть подзадачи - переходим к ним
            self.navigate_to_subtasks(note_data)
        else:
            # Нет подзадач - создаем первую подзадачу n-го уровня
            self.create_first_subtask(note_data)
    
    def create_first_subtask(self, parent_note):
        """Создает первую подзадачу n-го уровня для указанной заметки"""
        if not self.current_task:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите задачу!")
            return
        
        # Создаем диалог для создания подзадачи n-го уровня
        dialog = NoteEditor(self.current_task, parent_note[0])  # parent_note[0] - это ID родительской заметки
        if dialog.exec_() == QDialog.Accepted:
            # После создания подзадачи, переходим к просмотру подзадач
            self.navigate_to_subtasks(parent_note)
    
    def navigate_to_subtasks(self, parent_note):
        """Переходит к подзадачам указанной заметки"""
        # Сохраняем текущее состояние в стек навигации
        self.navigation_stack.append({
            'current_task': self.current_task,
            'current_parent_note': self.current_parent_note
        })
        
        # Устанавливаем новую родительскую заметку
        self.current_parent_note = parent_note
        
        # Обновляем интерфейс
        self.update_navigation_ui()
        self.load_notes()
    
    def go_back_to_parent(self):
        """Возвращается к родительской заметке"""
        if self.navigation_stack:
            # Восстанавливаем предыдущее состояние
            prev_state = self.navigation_stack.pop()
            self.current_task = prev_state['current_task']
            self.current_parent_note = prev_state['current_parent_note']
            
            # Обновляем интерфейс
            self.update_navigation_ui()
            self.load_notes()
    
    def update_navigation_ui(self):
        """Обновляет панель навигации"""
        if self.current_parent_note:
            # Показываем панель навигации
            self.navigation_frame.show()
            
            # Обновляем текст навигации
            parent_title = self.current_parent_note[2]  # title
            if len(parent_title) > 30:
                parent_title = parent_title[:27] + "..."
            
            self.navigation_label.setText(f"📁 Подзадачи: {parent_title}")
            
            # Обновляем кнопку добавления заметки
            self.add_note_button.setText("➕ Добавить подзадачу n-го уровня")
        else:
            # Скрываем панель навигации
            self.navigation_frame.hide()
            self.add_note_button.setText("➕ Добавить подзаметку")
    
    def show_context_menu(self, pos):
        """Показывает контекстное меню"""
        item = self.notes_list.itemAt(pos)
        if not item or not item.data(Qt.UserRole):
            return
        
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
            }
            QMenu::item:selected {
                background-color: #1f7a57;
                color: white;
            }
        """)
        
        delete_action = menu.addAction("🗑️ Удалить")
        
        action = menu.exec_(self.notes_list.mapToGlobal(pos))
        
        if action == delete_action:
            self.delete_note(item)
    
    def delete_note(self, item):
        """Удаляет заметку"""
        note_data = item.data(Qt.UserRole)
        if not note_data:
            return
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                   f"Вы уверены, что хотите удалить заметку '{note_data[1]}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                delete_note(note_data[0])
                self.load_notes()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить заметку: {str(e)}")
