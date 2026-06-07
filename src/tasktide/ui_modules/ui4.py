import sys
import sqlite3
from src.tasktide.paths import get_db_path
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QFrame, QSizePolicy, QListWidget, QListWidgetItem, QMenu,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from src.tasktide.styles import get_default_style


class StatisticsWindow(QMainWindow):
    def __init__(self, show_main_menu_callback=None):
        super().__init__()
        self.show_main_menu_callback = show_main_menu_callback
        self.setWindowTitle("Статистика")
        self.setGeometry(100, 100, 1200, 1000)  # Возвращаем исходную ширину
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной вертикальный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Создаем верхнюю панель с кнопками
        self.create_top_control_bar(main_layout)
        
        # Создаем центральную область с двумя панелями
        self.create_central_content_area(main_layout)
        
        # Создаем нижнюю панель
        self.create_bottom_section(main_layout)
        
        # Настройка стилей
        self.setup_styles()
    
    def create_top_control_bar(self, parent_layout):
        """Создает верхнюю панель с кнопками управления"""
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.Box)
        top_frame.setMaximumHeight(60)
        
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(10)
        
        # Кнопки управления
        self.back_btn = QPushButton("Назад")
        self.back_btn.clicked.connect(self.go_back)
        self.basic_btn = QPushButton("Базовая")
        self.basic_btn.clicked.connect(self.show_basic_functions)
        self.medium_btn = QPushButton("Средняя")
        self.medium_btn.clicked.connect(self.show_medium_functions)
        self.advanced_btn = QPushButton("Продвинутая")
        self.advanced_btn.clicked.connect(self.show_advanced_functions)
        
        # Добавляем кнопки в layout
        buttons = [self.back_btn, self.basic_btn, self.medium_btn, self.advanced_btn]
        for btn in buttons:
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            top_layout.addWidget(btn)
        
        parent_layout.addWidget(top_frame)
    
    def create_central_content_area(self, parent_layout):
        """Создает центральную область с двумя панелями"""
        central_frame = QFrame()
        central_frame.setFrameStyle(QFrame.Box)
        
        central_layout = QHBoxLayout(central_frame)
        central_layout.setSpacing(10)
        
        # Левая панель - окно с текстом
        self.text_panel = QFrame()
        self.text_panel.setFrameStyle(QFrame.Box)
        self.text_panel.setMinimumHeight(650)  # Еще больше увеличиваем высоту
        
        text_layout = QVBoxLayout(self.text_panel)
        text_label = QLabel("Данные")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: gray; font-size: 14px;")
        
        self.text_content = QTextEdit()
        self.text_content.setPlaceholderText("Здесь будет отображаться текстовая информация...")
        self.text_content.setMinimumHeight(600)  # Еще больше увеличиваем высоту текстового поля
        self.text_content.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Включаем прокрутку
        self.text_content.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Включаем горизонтальную прокрутку
        
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_content)
        
        # Правая панель - окно с графиком
        self.graph_panel = QFrame()
        self.graph_panel.setFrameStyle(QFrame.Box)
        self.graph_panel.setMinimumHeight(450)
        
        graph_layout = QVBoxLayout(self.graph_panel)
        
        # Создаем matplotlib canvas
        # Создаем PlotWidget для pyqtgraph
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('w')  # Белый фон
        self.plot_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }
        """)
        
        # Устанавливаем минимальный размер
        self.plot_widget.setMinimumSize(150, 100)
        
        graph_layout.addWidget(self.plot_widget)
        
        # PlotWidget видим по умолчанию
        self.plot_widget.show()
        
        # Декоративные элементы убраны, чтобы не перекрывать нижние границы
        
        # Добавляем панели в центральный layout
        central_layout.addWidget(self.text_panel, 1)
        central_layout.addWidget(self.graph_panel, 1)
        
        parent_layout.addWidget(central_frame, 1)
    
    
    def create_bottom_section(self, parent_layout):
        """Создает нижнюю секцию с информацией и кнопками"""
        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.Box)
        bottom_frame.setMaximumHeight(150)
        
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setSpacing(10)
        
        # Левая панель - окно с информацией
        self.info_panel = QFrame()
        self.info_panel.setFrameStyle(QFrame.Box)
        
        info_layout = QVBoxLayout(self.info_panel)
        info_label = QLabel("Вариант анализа")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; font-size: 14px;")
        
        # Список функций
        self.functions_list = QListWidget()
        self.functions_list.setMaximumHeight(80)
        self.functions_list.itemClicked.connect(self.on_function_selected)
        
        # По умолчанию показываем базовые функции
        self.show_basic_functions()
        
        info_layout.addWidget(info_label)
        info_layout.addWidget(self.functions_list)
        
        # Правая секция с кнопками
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(5)
        
        self.additional_btn = QPushButton("Дополнительно")
        self.refresh_btn = QPushButton("Актуально")
        
        # Подключаем обработчик для кнопки "Дополнительно"
        self.additional_btn.clicked.connect(self.show_additional_menu)
        
        # Подключаем обработчик клика для кнопки "Актуально"
        self.refresh_btn.clicked.connect(self.show_today_tasks)
        
        # Настройка кнопок
        for btn in [self.additional_btn, self.refresh_btn]:
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setMinimumWidth(120)
            buttons_layout.addWidget(btn)
        
        # Добавляем элементы в нижний layout
        bottom_layout.addWidget(self.info_panel, 1)
        bottom_layout.addWidget(buttons_frame)
        
        parent_layout.addWidget(bottom_frame)
    
    def setup_styles(self):
        """Настройка стилей для интерфейса"""
        self.setStyleSheet(get_default_style() + """
            QMainWindow {
                background-color: #f4f7fb;
            }
            QFrame {
                border: 1px solid #d9e2ec;
                background-color: #ffffff;
                border-radius: 12px;
            }
            QPushButton {
                background-color: #102a43;
                color: #f0f4f8;
                border: 1px solid #243b53;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #243b53;
            }
            QPushButton:pressed {
                background-color: #334e68;
            }
            QTextEdit {
                border: 1px solid #cfd9e5;
                border-radius: 10px;
                background-color: #ffffff;
                color: #102a43;
                font-size: 11px;
            }
        """)
    
    def go_back(self):
        """Возврат в главное меню"""
        if self.show_main_menu_callback:
            self.show_main_menu_callback()
    
    def show_basic_functions(self):
        """Показывает базовые функции статистики"""
        # Очищаем список и добавляем базовые функции
        self.functions_list.clear()
        functions = [
            "1) Общая сводка",
            "2) Текущий день / неделя", 
            "3) Динамика продуктивности",
            "4) Планирование и дедлайны"
        ]
        for func in functions:
            self.functions_list.addItem(func)
    
    def show_medium_functions(self):
        """Показывает функции средней сложности"""
        # Очищаем список и добавляем функции средней сложности
        self.functions_list.clear()
        functions = [
            "1) Показатели продуктивности",
            "2) Активные часы пользователя",
            "3) Приоритеты",
            "4) Нагрузка"
        ]
        for func in functions:
            self.functions_list.addItem(func)
    
    def on_function_selected(self, item):
        """Обрабатывает выбор функции из списка"""
        function_text = item.text()
        
        # Базовые функции
        if "Общая сводка" in function_text:
            self.show_general_summary()
        elif "Текущий день / неделя" in function_text:
            self.show_daily_weekly_dashboard()
        elif "Динамика продуктивности" in function_text:
            self.show_productivity_dynamics()
        elif "Планирование и дедлайны" in function_text:
            self.show_planning_deadlines()
        
        # Функции средней сложности
        elif "Показатели продуктивности" in function_text:
            self.show_productivity_metrics()
        elif "Активные часы пользователя" in function_text:
            self.show_active_hours()
        elif "Приоритеты" in function_text:
            self.show_priorities()
        elif "Нагрузка" in function_text:
            self.show_workload()

        # Продвинутые функции
        elif "1)" in function_text or "Карта активности" in function_text:
            self.show_activity_map()
        elif "2)" in function_text or "Прогноз продуктивности" in function_text:
            self.show_productivity_forecast()
        elif "3)" in function_text or "Аналитика времени" in function_text:
            self.show_time_analytics()
        elif "4)" in function_text or "Сравнение периодов" in function_text:
            self.show_period_comparison()
    
    def get_tasks_statistics(self):
        """Получает статистику по задачам из базы данных"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Общее количество задач
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        # Выполненные задачи
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'выполнена'")
        completed_tasks = cursor.fetchone()[0]
        
        # Задачи в процессе
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'в процессе'")
        in_progress_tasks = cursor.fetchone()[0]
        
        # Не начатые задачи
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'не начата'")
        not_started_tasks = cursor.fetchone()[0]
        
        # Просроченные задачи
        now = datetime.now()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE deadline < ? AND status != 'выполнена'", (now,))
        overdue_tasks = cursor.fetchone()[0]
        
        conn.close()
        
        # Рассчитываем процент выполнения
        completed_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total': total_tasks,
            'completed': completed_tasks,
            'completed_percent': completed_percent,
            'in_progress': in_progress_tasks,
            'not_started': not_started_tasks,
            'overdue': overdue_tasks
        }
    
    def get_category_statistics(self):
        """Получает статистику по категориям"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Получаем все задачи и группируем их правильно
        cursor.execute("SELECT category1, status FROM tasks")
        all_tasks = cursor.fetchall()
        
        # Словарь для группировки по очищенным категориям
        category_dict = {}
        
        for category, status in all_tasks:
            # Убираем иконки для правильной группировки
            clean_category = category
            for icon in ['🔥', '⭐', '⚡', '📝', '💼', '📚', '👤', '🏠']:
                clean_category = clean_category.replace(icon, '').strip()
            
            # Инициализируем категорию если её нет
            if clean_category not in category_dict:
                category_dict[clean_category] = {'total': 0, 'completed': 0}
            
            # Увеличиваем счетчики
            category_dict[clean_category]['total'] += 1
            if status == 'выполнена':
                category_dict[clean_category]['completed'] += 1
        
        # Преобразуем в словарь для удобства использования
        category_stats = {}
        for category, stats in category_dict.items():
            category_stats[category] = stats['total']
        
        conn.close()
        return category_stats
    
    def get_daily_statistics(self):
        """Получает статистику по текущему дню"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Получаем задачи на сегодня (с дедлайном сегодня или без дедлайна)
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_today,
                SUM(CASE WHEN status = 'выполнена' THEN 1 ELSE 0 END) as completed_today,
                SUM(CASE WHEN status != 'выполнена' AND (deadline IS NULL OR deadline <= ?) THEN 1 ELSE 0 END) as overdue_today
            FROM tasks 
            WHERE deadline IS NULL OR deadline <= ?
        """, (today, today))
        
        result = cursor.fetchone()
        conn.close()
        
        total_today = result[0] or 0
        completed_today = result[1] or 0
        overdue_today = result[2] or 0
        remaining_today = total_today - completed_today
        
        return {
            'total_today': total_today,
            'completed_today': completed_today,
            'remaining_today': remaining_today,
            'overdue_today': overdue_today
        }
    
    def get_weekly_statistics(self):
        """Получает статистику по текущей неделе"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Получаем начало и конец текущей недели
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_str = start_of_week.strftime('%Y-%m-%d')
        end_str = end_of_week.strftime('%Y-%m-%d')
        
        # Получаем общую статистику за неделю
        cursor.execute("""
            SELECT 
                COUNT(*) as total_week,
                SUM(CASE WHEN status = 'выполнена' THEN 1 ELSE 0 END) as completed_week
            FROM tasks 
            WHERE deadline IS NULL OR (deadline >= ? AND deadline <= ?)
        """, (start_str, end_str))
        
        result = cursor.fetchone()
        
        # Получаем статистику по дням недели для расчета среднего процента
        cursor.execute("""
            SELECT 
                DATE(deadline) as task_date,
                COUNT(*) as daily_total,
                SUM(CASE WHEN status = 'выполнена' THEN 1 ELSE 0 END) as daily_completed
            FROM tasks 
            WHERE deadline IS NOT NULL AND deadline >= ? AND deadline <= ?
            GROUP BY DATE(deadline)
        """, (start_str, end_str))
        
        daily_results = cursor.fetchall()
        conn.close()
        
        total_week = result[0] or 0
        completed_week = result[1] or 0
        
        # Рассчитываем средний процент выполнения по дням
        daily_completion_rates = []
        for date, daily_total, daily_completed in daily_results:
            if daily_total > 0:
                completion_rate = (daily_completed / daily_total) * 100
                daily_completion_rates.append(completion_rate)
        
        avg_completion = sum(daily_completion_rates) / len(daily_completion_rates) if daily_completion_rates else 0
        
        return {
            'total_week': total_week,
            'completed_week': completed_week,
            'avg_completion': avg_completion,
            'daily_data': daily_results
        }
    
    def get_deadline_statistics(self):
        """Получает статистику по дедлайнам"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        # Начало и конец текущей недели
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Задачи на сегодня (используем DATE() для извлечения только даты)
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE DATE(deadline) = DATE(?)", (today.strftime('%Y-%m-%d'),))
        today_count = cursor.fetchone()[0] or 0
        
        # Задачи на завтра
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE DATE(deadline) = DATE(?)", (tomorrow.strftime('%Y-%m-%d'),))
        tomorrow_count = cursor.fetchone()[0] or 0
        
        # Задачи на этой неделе
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE DATE(deadline) >= DATE(?) AND DATE(deadline) <= DATE(?)", 
                      (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')))
        this_week_count = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'today': today_count,
            'tomorrow': tomorrow_count,
            'this_week': this_week_count
        }
    
    def get_workload_statistics(self):
        """Получает статистику по нагрузке и трендам"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Получаем общее количество задач
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0] or 0
        
        # Поскольку у нас нет created_date, используем приблизительные расчеты
        # Предполагаем, что задачи создавались в течение последних 30 дней
        estimated_days = 30
        estimated_weeks = estimated_days / 7
        
        avg_daily = total_tasks / estimated_days if estimated_days > 0 else 0
        avg_weekly = total_tasks / estimated_weeks if estimated_weeks > 0 else 0
        
        # Для тренда используем анализ по дедлайнам (задачи с дедлайнами на ближайшие недели)
        today = datetime.now()
        one_week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)
        
        # Задачи с дедлайнами на ближайшую неделю
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE DATE(deadline) >= DATE(?) AND DATE(deadline) <= DATE(?)", 
                      (today.strftime('%Y-%m-%d'), (today + timedelta(days=7)).strftime('%Y-%m-%d')))
        current_week_tasks = cursor.fetchone()[0] or 0
        
        # Задачи с дедлайнами на следующую неделю
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE DATE(deadline) >= DATE(?) AND DATE(deadline) <= DATE(?)", 
                      ((today + timedelta(days=7)).strftime('%Y-%m-%d'), (today + timedelta(days=14)).strftime('%Y-%m-%d')))
        next_week_tasks = cursor.fetchone()[0] or 0
        
        # Рассчитываем тренд на основе планирования
        if current_week_tasks > 0:
            trend = ((next_week_tasks - current_week_tasks) / current_week_tasks) * 100
        else:
            trend = 100 if next_week_tasks > 0 else 0
        
        conn.close()
        
        return {
            'avg_daily': avg_daily,
            'avg_weekly': avg_weekly,
            'trend': trend
        }
    
    def get_plan_fact_statistics(self):
        """Получает статистику План vs Факт"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Всего задач с дедлайнами (план)
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE deadline IS NOT NULL")
        planned = cursor.fetchone()[0] or 0
        
        # Выполненные задачи с дедлайнами
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE deadline IS NOT NULL AND status = 'выполнена'")
        completed = cursor.fetchone()[0] or 0
        
        # Процент выполнения
        completion_rate = (completed / planned * 100) if planned > 0 else 0
        
        # Индикатор выполнения
        if completion_rate <= 50:
            indicator = "🔵 Низкое"
        elif completion_rate <= 80:
            indicator = "🟡 Среднее"
        else:
            indicator = "🟢 Отличное"
        
        conn.close()
        
        return {
            'planned': planned,
            'completed': completed,
            'completion_percent': completion_rate,
            'indicator': indicator
        }
    
    def show_general_summary(self):
        """Показывает общую сводку в текстовом окне"""
        stats = self.get_tasks_statistics()
        
        # Более компактный формат
        completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        summary_text = f"""📊 ОБЩАЯ СВОДКА

📋 Всего: {stats['total']} задач
✅ Выполнено: {stats['completed']} ({completion_rate:.1f}%)
🔄 В процессе: {stats['in_progress']}
⏳ Не начато: {stats['not_started']}
⚠️ Просрочено: {stats['overdue']}"""
        
        self.text_content.setPlainText(summary_text)
        
        # Создаем диаграмму по статусам задач
        status_data = [
            ('Выполнено', stats['completed']),
            ('В процессе', stats['in_progress']),
            ('Не начато', stats['not_started']),
            ('Просрочено', stats['overdue'])
        ]
        self.create_pie_chart(stats)
    
    def show_daily_weekly_dashboard(self):
        """Показывает мини-дашборд текущего дня и недели"""
        daily_stats = self.get_daily_statistics()
        weekly_stats = self.get_weekly_statistics()
        
        dashboard_text = "📅 МИНИ-ДАШБОРД\n\n"
        
        # Мини-дашборд текущего дня - более компактно
        dashboard_text += "🌅 СЕГОДНЯ:\n"
        dashboard_text += f"• Всего: {daily_stats['total_today']}, выполнено: {daily_stats['completed_today']}\n"
        dashboard_text += f"• Осталось: {daily_stats['remaining_today']}\n"
        
        if daily_stats['overdue_today'] > 0:
            dashboard_text += f"• Просрочено: {daily_stats['overdue_today']}\n"
        else:
            dashboard_text += "• Просроченных нет\n"
        
        dashboard_text += "\n📊 НЕДЕЛЯ:\n"
        dashboard_text += f"• Всего: {weekly_stats['total_week']}\n"
        dashboard_text += f"• Средний %: {weekly_stats['avg_completion']:.1f}%\n"
        
        if weekly_stats['completed_week'] > 0:
            dashboard_text += f"• Выполнено: {weekly_stats['completed_week']}\n"
        
        self.text_content.setPlainText(dashboard_text)
        
        # Создаем диаграмму по дням недели
        self.create_weekly_chart(weekly_stats)
    
    def create_pie_chart(self, stats):
        """Создает простую столбчатую диаграмму с помощью pyqtgraph"""
        # Очищаем предыдущий график
        self.plot_widget.clear()
        
        # Подготавливаем данные
        labels = ['Выполнено', 'В процессе', 'Не начато']
        sizes = [stats['completed'], stats['in_progress'], stats['not_started']]
        
        # Убираем нулевые значения
        filtered_data = []
        filtered_labels = []
        
        for i, size in enumerate(sizes):
            if size > 0:
                filtered_data.append(size)
                filtered_labels.append(labels[i])
        
        if not filtered_data:
            # Заглушка если нет данных
            text = pg.TextItem('Нет данных', color='gray', anchor=(0.5, 0.5))
            self.plot_widget.addItem(text)
            text.setPos(0, 0)
        else:
            # Создаем простую столбчатую диаграмму
            x = list(range(len(filtered_data)))
            y = filtered_data
            
            # Создаем столбцы с разными цветами
            colors = ['g', 'orange', 'r']  # Простые цвета
            for i, (xi, yi) in enumerate(zip(x, y)):
                color = colors[i] if i < len(colors) else 'b'
                bg = pg.BarGraphItem(x=[xi], height=[yi], width=0.6, brush=pg.mkBrush(color))
                self.plot_widget.addItem(bg)
            
            # Добавляем подписи
            for i, (label, value) in enumerate(zip(filtered_labels, filtered_data)):
                text = pg.TextItem(f'{label}\n{value}', anchor=(0.5, 1))
                self.plot_widget.addItem(text)
                text.setPos(i, value + 0.5)
        
        # Настраиваем вид
        self.plot_widget.setXRange(-0.5, len(filtered_data) - 0.5)
        self.plot_widget.setYRange(0, max(filtered_data) + 2 if filtered_data else 5)
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Статус задач')  # Убрано по запросу пользователя
        self.plot_widget.showGrid(x=True, y=True)
    
    def clear_graph(self):
        """Очищает график"""
        self.plot_widget.clear()
    
    
    def create_line_chart(self, history_data):
        """Создает линейный график динамики продуктивности"""
        # Очищаем предыдущий график
        self.plot_widget.clear()
        
        if not history_data:
            # Заглушка если нет данных
            text = pg.TextItem('Нет данных', color='gray', anchor=(0.5, 0.5))
            self.plot_widget.addItem(text)
            text.setPos(0, 0)
            return
        
        # Подготавливаем данные
        dates = []
        values = []
        
        for day, completed in history_data:
            # Преобразуем дату в более короткий формат
            date_parts = day.split('-')
            short_date = f"{date_parts[2]}.{date_parts[1]}"  # ДД.ММ
            dates.append(short_date)
            values.append(completed)
        
        # Создаем линейный график
        x = list(range(len(dates)))
        y = values
        
        # Создаем линию
        line = pg.PlotDataItem(x, y, pen=pg.mkPen('b', width=3), symbol='o', symbolSize=8)
        self.plot_widget.addItem(line)
        
        # Добавляем подписи к точкам
        for i, (date, value) in enumerate(zip(dates, values)):
            text = pg.TextItem(f'{value}', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(i, value + 0.5)
        
        # Настраиваем вид
        self.plot_widget.setXRange(-0.5, len(dates) - 0.5)
        self.plot_widget.setYRange(0, max(values) + 2 if values else 5)
        # self.plot_widget.setLabel('left', 'Выполнено задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Дни')  # Убрано по запросу пользователя
        self.plot_widget.showGrid(x=True, y=True)
        
        # Устанавливаем подписи по оси X
        ticks = [(i, date) for i, date in enumerate(dates)]
        self.plot_widget.getAxis('bottom').setTicks([ticks])
    
    def create_category_chart(self, category_data):
        """Создает столбчатую диаграмму по категориям"""
        # Очищаем предыдущий график
        self.plot_widget.clear()
        
        if not category_data:
            # Заглушка если нет данных
            text = pg.TextItem('Нет данных', color='gray', anchor=(0.5, 0.5))
            self.plot_widget.addItem(text)
            text.setPos(0, 0)
            return
        
        # Подготавливаем данные
        categories = [item[0] for item in category_data]
        values = [item[1] for item in category_data]
        
        # Создаем столбчатую диаграмму
        x = list(range(len(categories)))
        colors = ['g', 'orange', 'r', 'b', 'purple', 'brown', 'pink', 'gray']
        
        for i, (cat, val) in enumerate(zip(categories, values)):
            color = colors[i % len(colors)]
            bg = pg.BarGraphItem(x=[x[i]], height=[val], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            # Добавляем подпись с названием категории и значением
            text = pg.TextItem(f'{cat}\n{val}', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], val + 0.1)
        
        # Настраиваем график
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Категории')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(categories) - 0.5)
        self.plot_widget.setYRange(0, max(values) * 1.2)
        self.plot_widget.showGrid(x=True, y=True)
    
    def create_weekly_chart(self, weekly_stats):
        """Создает диаграмму по дням недели"""
        self.plot_widget.clear()
        
        if not weekly_stats['daily_data']:
            # Заглушка если нет данных
            text = pg.TextItem('Нет данных за неделю', color='gray', anchor=(0.5, 0.5))
            self.plot_widget.addItem(text)
            text.setPos(0, 0)
            return
        
        # Подготавливаем данные по дням
        daily_data = weekly_stats['daily_data']
        dates = []
        completion_rates = []
        
        for date, daily_total, daily_completed in daily_data:
            dates.append(date)
            completion_rate = (daily_completed / daily_total) * 100 if daily_total > 0 else 0
            completion_rates.append(completion_rate)
        
        # Создаем линейный график
        x = list(range(len(dates)))
        
        # Создаем линию
        line = pg.PlotDataItem(x, completion_rates, pen=pg.mkPen('blue', width=3))
        self.plot_widget.addItem(line)
        
        # Добавляем точки
        for i, (date, rate) in enumerate(zip(dates, completion_rates)):
            point = pg.ScatterPlotItem([i], [rate], pen=pg.mkPen('blue', width=2), 
                                     brush=pg.mkBrush('lightblue'), size=10)
            self.plot_widget.addItem(point)
            
            # Добавляем подпись с датой и процентом
            text = pg.TextItem(f'{date}\n{rate:.1f}%', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(i, rate + 2)
        
        # Настраиваем график
        # self.plot_widget.setLabel('left', 'Процент выполнения (%)')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Дни недели')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(dates) - 0.5)
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.showGrid(x=True, y=True)
    
    def create_deadline_chart(self, deadline_stats):
        """Создает диаграмму по дедлайнам"""
        self.plot_widget.clear()
        
        # Подготавливаем данные
        categories = ['Сегодня', 'Завтра', 'Эта неделя']
        values = [
            deadline_stats['today'],
            deadline_stats['tomorrow'],
            deadline_stats['this_week']
        ]
        
        # Создаем столбчатую диаграмму
        x = list(range(len(categories)))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # Красный, бирюзовый, синий
        
        for i, (cat, val) in enumerate(zip(categories, values)):
            color = colors[i]
            bg = pg.BarGraphItem(x=[x[i]], height=[val], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            # Добавляем подпись с названием и значением
            text = pg.TextItem(f'{cat}\n{val}', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], val + 0.1)
        
        # Настраиваем график
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Период')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(categories) - 0.5)
        self.plot_widget.setYRange(0, max(values) * 1.2 if values else 5)
        self.plot_widget.showGrid(x=True, y=True)
    
    # Функции средней сложности
    def show_productivity_metrics(self):
        """Показывает показатели продуктивности"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Получаем общую статистику
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'выполнена'")
            completed_tasks = cursor.fetchone()[0] or 0
            
            # Рассчитываем показатели
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Получаем статистику по дням недели
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN deadline IS NULL THEN 'Без дедлайна'
                        WHEN DATE(deadline) = DATE('now') THEN 'Сегодня'
                        WHEN DATE(deadline) = DATE('now', '+1 day') THEN 'Завтра'
                        WHEN DATE(deadline) BETWEEN DATE('now') AND DATE('now', '+7 days') THEN 'Эта неделя'
                        ELSE 'Будущее'
                    END as period,
                    COUNT(*) as count,
                    SUM(CASE WHEN status = 'выполнена' THEN 1 ELSE 0 END) as completed
                FROM tasks 
                GROUP BY period
                ORDER BY 
                    CASE period
                        WHEN 'Сегодня' THEN 1
                        WHEN 'Завтра' THEN 2
                        WHEN 'Эта неделя' THEN 3
                        WHEN 'Будущее' THEN 4
                        WHEN 'Без дедлайна' THEN 5
                    END
            """)
            
            period_data = cursor.fetchall()
            conn.close()
            
            metrics_text = "📊 ПОКАЗАТЕЛИ ПРОДУКТИВНОСТИ\n\n"
            # Более компактный формат общей статистики
            metrics_text += f"🎯 Выполнение: {completion_rate:.1f}% ({completed_tasks}/{total_tasks})\n"
            metrics_text += f"🔄 В работе: {total_tasks - completed_tasks}\n\n"
            
            metrics_text += "📅 По периодам:\n"
            for period, count, completed in period_data:
                period_completion = (completed / count * 100) if count > 0 else 0
                # Более компактный формат
                metrics_text += f"• {period}: {count} ({period_completion:.0f}%)\n"
            
            self.text_content.setPlainText(metrics_text)
            
            # Создаем диаграмму показателей
            self.create_productivity_metrics_chart(period_data)
            
        except Exception as e:
            error_text = f"Ошибка при загрузке показателей продуктивности:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def show_active_hours(self):
        """Показывает активные часы пользователя"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Получаем статистику по времени создания задач (приблизительно)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status = 'выполнена' THEN 1 ELSE 0 END) as completed_tasks
                FROM tasks
            """)
            
            result = cursor.fetchone()
            total_tasks = result[0] or 0
            completed_tasks = result[1] or 0
            
            # Симулируем активные часы на основе данных
            active_hours_text = "⏰ АКТИВНЫЕ ЧАСЫ ПОЛЬЗОВАТЕЛЯ\n\n"
            active_hours_text += "📊 Анализ активности (на основе задач):\n\n"
            
            # Рассчитываем примерные часы активности
            if total_tasks > 0:
                estimated_hours = total_tasks * 0.5  # Примерно 30 минут на задачу
                active_hours_text += f"🕐 Примерное время работы: {estimated_hours:.1f} часов\n"
                active_hours_text += f"📈 Средняя продуктивность: {completed_tasks / total_tasks * 100:.1f}%\n\n"
                
                # Распределение по "часам дня" (симуляция)
                hours_distribution = [
                    ("Утро (6-12)", total_tasks * 0.3),
                    ("День (12-18)", total_tasks * 0.4),
                    ("Вечер (18-24)", total_tasks * 0.3)
                ]
                
                active_hours_text += "🌅 Распределение активности по времени:\n"
                for period, tasks in hours_distribution:
                    active_hours_text += f"• {period}: {tasks:.0f} задач\n"
            else:
                active_hours_text += "📝 Нет данных для анализа активности\n"
            
            self.text_content.setPlainText(active_hours_text)
            
            # Создаем диаграмму активных часов
            if total_tasks > 0:
                self.create_active_hours_chart(hours_distribution)
            else:
                self.clear_graph()
                
        except Exception as e:
            error_text = f"Ошибка при загрузке активных часов:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def show_priorities(self):
        """Показывает анализ приоритетов (матрица Эйзенхауэра)"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Получаем все задачи и группируем их по приоритетам (category1)
            cursor.execute("SELECT category1, status FROM tasks")
            all_tasks = cursor.fetchall()
            
            # Словарь для группировки по очищенным приоритетам
            priority_dict = {}
            
            # Список валидных приоритетов из матрицы Эйзенхауэра
            valid_priorities = ['Важно - Срочно', 'Важно - Не срочно', 'Не важно - Срочно', 'Не важно - Не срочно']
            
            for category1, status in all_tasks:
                # Убираем иконки для правильной группировки
                clean_priority = category1
                for icon in ['🔥', '⭐', '⚡', '📝', '💼', '📚', '👤', '🏠']:
                    clean_priority = clean_priority.replace(icon, '').strip()
                
                # Проверяем, что приоритет входит в матрицу Эйзенхауэра
                if clean_priority in valid_priorities:
                    # Инициализируем приоритет если его нет
                    if clean_priority not in priority_dict:
                        priority_dict[clean_priority] = {'total': 0, 'completed': 0}
                    
                    # Увеличиваем счетчики
                    priority_dict[clean_priority]['total'] += 1
                    if status == 'выполнена':
                        priority_dict[clean_priority]['completed'] += 1
            
            # Преобразуем в список кортежей и сортируем по важности
            priority_data = []
            for priority, stats in priority_dict.items():
                priority_data.append((priority, stats['total'], stats['completed']))
            
            # Сортируем по важности (матрица Эйзенхауэра)
            priority_order = {
                'Важно - Срочно': 1,
                'Важно - Не срочно': 2,
                'Не важно - Срочно': 3,
                'Не важно - Не срочно': 4
            }
            priority_data.sort(key=lambda x: priority_order.get(x[0], 5))
            
            conn.close()
            
            priorities_text = "🎯 ПРИОРИТЕТЫ (МАТРИЦА ЭЙЗЕНХАУЭРА)\n\n"
            
            if priority_data:
                total_tasks = sum(item[1] for item in priority_data)
                total_completed = sum(item[2] for item in priority_data)
                
                # Очень компактный формат общей статистики
                completion_rate = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
                priorities_text += f"📊 {total_tasks} задач, {total_completed} выполнено ({completion_rate:.0f}%)\n\n"
                
                priorities_text += "🎯 По приоритетам:\n"
                for priority, total, completed in priority_data:
                    completion_rate = (completed / total * 100) if total > 0 else 0
                    percentage = (total / total_tasks * 100) if total_tasks > 0 else 0
                    
                    # Добавляем эмодзи для визуального различения
                    priority_emoji = {
                        'Важно - Срочно': '🔥',
                        'Важно - Не срочно': '⭐',
                        'Не важно - Срочно': '⚡',
                        'Не важно - Не срочно': '📝'
                    }
                    emoji = priority_emoji.get(priority, '📋')
                    
                    # Сокращаем названия приоритетов
                    short_priority = priority.replace('Важно - ', 'В-').replace('Не важно - ', 'НВ-').replace('Срочно', 'С').replace('Не срочно', 'НС')
                    
                    # Очень компактный формат
                    priorities_text += f"• {emoji} {short_priority}: {total} ({percentage:.0f}%) - {completed}/{total} ({completion_rate:.0f}%)\n"
                
                # Добавляем краткие рекомендации
                priorities_text += "\n💡 РЕКОМЕНДАЦИИ:\n"
                for priority, total, completed in priority_data:
                    if priority == 'Важно - Не срочно' and total > 0:
                        priorities_text += f"• В-НС: фокус на долгосрочный успех\n"
                    elif priority == 'Важно - Срочно' and total > 0:
                        priorities_text += f"• В-С: требует немедленного внимания\n"
                    elif priority == 'Не важно - Срочно' and total > 0:
                        priorities_text += f"• НВ-С: делегировать или минимизировать\n"
                    elif priority == 'Не важно - Не срочно' and total > 0:
                        priorities_text += f"• НВ-НС: избегать или в свободное время\n"
            else:
                priorities_text += "📝 Нет данных по приоритетам\n"
            
            self.text_content.setPlainText(priorities_text)
            
            # Создаем диаграмму приоритетов
            if priority_data:
                self.create_priorities_chart(priority_data)
            else:
                self.clear_graph()
                
        except Exception as e:
            error_text = f"Ошибка при загрузке приоритетов:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def show_workload(self):
        """Показывает анализ нагрузки"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Получаем статистику по категориям используя исправленную функцию
            category_data = self.get_category_statistics()
            
            # Получаем общую статистику
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'выполнена'")
            completed_tasks = cursor.fetchone()[0] or 0
            
            conn.close()
            
            workload_text = "📊 НАГРУЗКА\n\n"
            
            # Общая нагрузка
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            workload_text += f"📊 Общая нагрузка: {total_tasks} задач\n"
            workload_text += f"✅ Выполнено: {completed_tasks} ({completion_rate:.1f}%)\n"
            workload_text += f"🔄 В работе: {total_tasks - completed_tasks}\n\n"
            
            # Нагрузка по категориям
            if category_data:
                workload_text += "📋 По категориям:\n"
                for category, total in category_data.items():
                    # Получаем количество выполненных задач для этой категории
                    conn = sqlite3.connect(str(get_db_path()))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM tasks WHERE category1 LIKE ? AND status = 'выполнена'", (f'%{category}%',))
                    completed = cursor.fetchone()[0] or 0
                    conn.close()
                    
                    completion_rate = (completed / total * 100) if total > 0 else 0
                    percentage = (total / total_tasks * 100) if total_tasks > 0 else 0
                    
                    workload_text += f"• {category}: {total} ({percentage:.0f}%) - {completed}/{total} ({completion_rate:.0f}%)\n"
            else:
                workload_text += "📝 Нет данных по категориям\n"
            
            self.text_content.setPlainText(workload_text)
            
            # Создаем диаграмму нагрузки
            if category_data:
                self.create_workload_chart(category_data)
            else:
                self.clear_graph()
                
        except Exception as e:
            error_text = f"Ошибка при загрузке нагрузки:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    # Методы для создания диаграмм средней сложности
    def create_productivity_metrics_chart(self, period_data):
        """Создает диаграмму показателей продуктивности"""
        self.plot_widget.clear()
        
        if not period_data:
            text = pg.TextItem('Нет данных', color='gray', anchor=(0.5, 0.5))
            self.plot_widget.addItem(text)
            text.setPos(0, 0)
            return
        
        periods = [item[0] for item in period_data]
        completion_rates = [(item[2] / item[1] * 100) if item[1] > 0 else 0 for item in period_data]
        
        x = list(range(len(periods)))
        colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0']
        
        for i, (period, rate) in enumerate(zip(periods, completion_rates)):
            color = colors[i % len(colors)]
            bg = pg.BarGraphItem(x=[x[i]], height=[rate], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            text = pg.TextItem(f'{period}\n{rate:.1f}%', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], rate + 2)
        
        # self.plot_widget.setLabel('left', 'Процент выполнения (%)')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Период')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(periods) - 0.5)
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.showGrid(x=True, y=True)
    
    def create_active_hours_chart(self, hours_distribution):
        """Создает диаграмму активных часов"""
        self.plot_widget.clear()
        
        periods = [item[0] for item in hours_distribution]
        tasks = [item[1] for item in hours_distribution]
        
        x = list(range(len(periods)))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for i, (period, task_count) in enumerate(zip(periods, tasks)):
            color = colors[i % len(colors)]
            bg = pg.BarGraphItem(x=[x[i]], height=[task_count], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            text = pg.TextItem(f'{period}\n{task_count:.0f}', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], task_count + 0.5)
        
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Время дня')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(periods) - 0.5)
        self.plot_widget.setYRange(0, max(tasks) * 1.2 if tasks else 5)
        self.plot_widget.showGrid(x=True, y=True)
    
    def create_priorities_chart(self, priority_data):
        """Создает диаграмму приоритетов"""
        self.plot_widget.clear()
        
        priorities = [item[0] for item in priority_data]
        completion_rates = [(item[2] / item[1] * 100) if item[1] > 0 else 0 for item in priority_data]
        
        x = list(range(len(priorities)))
        # Цвета для матрицы Эйзенхауэра
        colors = ['#F44336', '#FF9800', '#2196F3', '#9C27B0']  # Красный, оранжевый, синий, фиолетовый
        
        for i, (priority, rate) in enumerate(zip(priorities, completion_rates)):
            color = colors[i % len(colors)]
            bg = pg.BarGraphItem(x=[x[i]], height=[rate], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            # Сокращаем названия приоритетов для лучшего отображения
            short_priority = priority.replace('Важно - ', 'В-').replace('Не важно - ', 'НВ-').replace('Срочно', 'С').replace('Не срочно', 'НС')
            text = pg.TextItem(f'{short_priority}\n{rate:.0f}%', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], rate + 2)
        
        # self.plot_widget.setLabel('left', 'Процент выполнения (%)')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Приоритет')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(priorities) - 0.5)
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.showGrid(x=True, y=True)
    
    def create_workload_chart(self, category_data):
        """Создает диаграмму нагрузки"""
        self.plot_widget.clear()
        
        categories = []
        totals = []
        completed = []
        
        for category, total in category_data.items():
            # Получаем количество выполненных задач для этой категории
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE category1 LIKE ? AND status = 'выполнена'", (f'%{category}%',))
            comp = cursor.fetchone()[0] or 0
            conn.close()
            
            categories.append(category)
            totals.append(total)
            completed.append(comp)
        
        x = list(range(len(categories)))
        colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0', '#9C27B0']
        
        # Создаем столбцы для общего количества
        for i, (cat, total) in enumerate(zip(categories, totals)):
            color = colors[i % len(colors)]
            bg = pg.BarGraphItem(x=[x[i]], height=[total], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            text = pg.TextItem(f'{cat}\n{total}', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], total + 0.5)
        
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Категория')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(categories) - 0.5)
        self.plot_widget.setYRange(0, max(totals) * 1.2 if totals else 5)
        self.plot_widget.showGrid(x=True, y=True)
    
    def show_productivity_dynamics(self):
        """Показывает динамику продуктивности"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Получаем общую статистику по выполненным задачам
        cursor.execute("""
            SELECT COUNT(*) as total_completed
            FROM tasks 
            WHERE status = 'выполнена'
        """)
        
        total_completed = cursor.fetchone()[0]
        
        # Получаем все выполненные задачи и группируем их правильно
        cursor.execute("SELECT category1 FROM tasks WHERE status = 'выполнена'")
        completed_tasks = cursor.fetchall()
        
        # Словарь для группировки по очищенным категориям
        category_dict = {}
        
        for (category,) in completed_tasks:
            # Убираем иконки для правильной группировки
            clean_category = category
            for icon in ['🔥', '⭐', '⚡', '📝', '💼', '📚', '👤', '🏠']:
                clean_category = clean_category.replace(icon, '').strip()
            
            # Увеличиваем счетчик
            if clean_category in category_dict:
                category_dict[clean_category] += 1
            else:
                category_dict[clean_category] = 1
        
        # Преобразуем в список и сортируем
        category_data = [(category, count) for category, count in category_dict.items()]
        category_data.sort(key=lambda x: x[1], reverse=True)
        conn.close()
        
        if total_completed == 0:
            self.text_content.setPlainText("Нет выполненных задач для анализа динамики")
            self.clear_graph()
            return
        
        dynamics_text = "📈 ДИНАМИКА ПРОДУКТИВНОСТИ\n\n"
        dynamics_text += f"✅ Выполнено: {total_completed} задач\n\n"
        dynamics_text += "📊 По категориям:\n"
        
        for category, count in category_data:
            percentage = (count / total_completed) * 100
            dynamics_text += f"• {category}: {count} ({percentage:.0f}%)\n"
        
        self.text_content.setPlainText(dynamics_text)
        
        # Создаем простой график по категориям
        self.create_category_chart(category_data)
    
    def show_planning_deadlines(self):
        """Показывает анализ планирования и дедлайнов"""
        try:
            deadline_stats = self.get_deadline_statistics()
            workload_stats = self.get_workload_statistics()
            plan_fact_stats = self.get_plan_fact_statistics()
            
            planning_text = "📅 ПЛАНИРОВАНИЕ И ДЕДЛАЙНЫ\n\n"
            
            # 📅 Задачи по дедлайнам - более компактно
            planning_text += "📅 По дедлайнам:\n"
            planning_text += f"• Сегодня: {deadline_stats['today']}\n"
            planning_text += f"• Завтра: {deadline_stats['tomorrow']}\n"
            planning_text += f"• Эта неделя: {deadline_stats['this_week']}\n\n"
            
            # 📈 Средняя нагрузка - более компактно
            planning_text += "📈 Нагрузка:\n"
            planning_text += f"• Средне: {workload_stats['avg_daily']:.1f}/день, {workload_stats['avg_weekly']:.1f}/неделю\n"
            planning_text += f"• Тренд: {workload_stats['trend']:+.1f}%\n\n"
            
            # 📊 План vs Факт - более компактно
            completion_rate = plan_fact_stats['completion_percent']
            planning_text += "📊 План vs Факт:\n"
            planning_text += f"• План: {plan_fact_stats['planned']}, выполнено: {plan_fact_stats['completed']}\n"
            planning_text += f"• Процент: {completion_rate:.1f}%\n"
            
            # Индикатор выполнения - более компактно
            if completion_rate <= 50:
                indicator = "🔵 Низкое"
            elif completion_rate <= 80:
                indicator = "🟡 Среднее"
            else:
                indicator = "🟢 Отличное"
            
            planning_text += f"• Уровень: {indicator}\n"
            
            self.text_content.setPlainText(planning_text)
            
            # Создаем диаграмму по дедлайнам
            self.create_deadline_chart(deadline_stats)
            
        except Exception as e:
            error_text = f"Ошибка при загрузке данных планирования:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()


    def show_advanced_functions(self):
        """Показывает продвинутые функции статистики"""
        # Очищаем список функций
        self.functions_list.clear()
        
        # Добавляем продвинутые функции
        advanced_functions = [
            "1) Карта активности за месяц",
            "2) Прогноз продуктивности", 
            "3) Аналитика времени",
            "4) Сравнение периодов"
        ]
        
        for func in advanced_functions:
            item = QListWidgetItem(func)
            self.functions_list.addItem(item)
        
        # Очищаем текстовую область и график
        self.text_content.clear()
        self.clear_graph()
    
    def show_activity_map(self):
        """Показывает карту активности за месяц"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Получаем данные о выполненных задачах за последние 30 дней
            # Используем updated_at для получения даты выполнения задачи
            cursor.execute("""
                SELECT 
                    date(updated_at) as task_date,
                    COUNT(*) as completed_tasks
                FROM tasks 
                WHERE status = 'выполнена' 
                AND date(updated_at) >= date('now', '-30 days')
                GROUP BY date(updated_at)
                ORDER BY task_date
            """)
            
            activity_data = cursor.fetchall()
            conn.close()
            
            activity_text = ""
            
            # Создаем словарь для быстрого поиска
            activity_dict = {date: count for date, count in activity_data}
            
            # Получаем диапазон дат - показываем полные 30 дней
            today = datetime.now().date()
            start_date = today - timedelta(days=29)
            
            # Показываем активность по дням - ВСЕ 30 дней в 2 столбца
            current_date = start_date
            days_data = []
            
            # Собираем данные для всех дней
            for day_num in range(30):  # Гарантированно 30 дней
                date_str = current_date.strftime("%Y-%m-%d")
                day_name = current_date.strftime("%a")
                count = activity_dict.get(date_str, 0)
                
                # Создаем визуальную индикацию активности
                if count == 0:
                    indicator = "⚪"
                elif count <= 2:
                    indicator = "🟡"
                elif count <= 5:
                    indicator = "🟠"
                else:
                    indicator = "🟢"
                
                days_data.append(f"{indicator} {day_name} {current_date.strftime('%d.%m')}: {count} задач")
                current_date += timedelta(days=1)
            
            # Форматируем в 2 столбца
            for i in range(0, len(days_data), 2):
                if i + 1 < len(days_data):
                    # Два дня в строке
                    activity_text += f"{days_data[i]:<25} {days_data[i+1]}\n"
                else:
                    # Последний день, если нечетное количество
                    activity_text += f"{days_data[i]}\n"
            
            
            self.text_content.setPlainText(activity_text)
            
            # Создаем график активности
            if activity_data:
                self.create_activity_chart(activity_data)
            else:
                self.clear_graph()
                
        except Exception as e:
            error_text = f"Ошибка при загрузке карты активности:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def show_productivity_forecast(self):
        """Показывает прогноз продуктивности"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Получаем историю выполнения задач за последние 30 дней
            cursor.execute("""
                SELECT 
                    date(updated_at) as task_date,
                    COUNT(*) as completed_tasks
                FROM tasks 
                WHERE status = 'выполнена' 
                AND date(updated_at) >= date('now', '-30 days')
                GROUP BY date(updated_at)
                ORDER BY task_date
            """)
            
            history_data = cursor.fetchall()
            conn.close()
            
            forecast_text = "📈 ПРОГНОЗ ПРОДУКТИВНОСТИ\n\n"
            
            if history_data and len(history_data) >= 7:
                # Вычисляем тренд
                dates = [datetime.strptime(date, "%Y-%m-%d").date() for date, _ in history_data]
                tasks = [count for _, count in history_data]
                
                # Простой линейный тренд
                n = len(tasks)
                x_sum = sum(range(n))
                y_sum = sum(tasks)
                xy_sum = sum(i * tasks[i] for i in range(n))
                x2_sum = sum(i * i for i in range(n))
                
                if n > 1:
                    slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
                    intercept = (y_sum - slope * x_sum) / n
                else:
                    slope = 0
                    intercept = tasks[0] if tasks else 0
                
                # Прогноз на неделю вперед
                today = datetime.now().date()
                week_forecast = []
                for i in range(7):
                    future_day = today + timedelta(days=i+1)
                    predicted_tasks = max(0, slope * (n + i) + intercept)
                    week_forecast.append((future_day, predicted_tasks))
                
                # Прогноз на месяц
                month_forecast = 0
                for i in range(30):
                    predicted_tasks = max(0, slope * (n + i) + intercept)
                    month_forecast += predicted_tasks
                
                forecast_text += "🔮 Прогноз на неделю:\n"
                for date, predicted in week_forecast:
                    day_name = date.strftime("%a")
                    forecast_text += f"• {day_name} {date.strftime('%d.%m')}: ~{predicted:.1f} задач\n"
                
                forecast_text += f"\n📊 Прогноз на месяц: ~{month_forecast:.0f} задач\n"
                
                # Анализ тренда
                if slope > 0.1:
                    trend = "📈 Растущий"
                elif slope < -0.1:
                    trend = "📉 Убывающий"
                else:
                    trend = "➡️ Стабильный"
                
                forecast_text += f"📈 Тренд: {trend}\n"
                
                # Сообщение с прогнозом
                if month_forecast > 0:
                    forecast_text += f"\n💡 Если темп сохранится, ты выполнишь ещё {month_forecast:.0f} задач в этом месяце.\n"
                
                # Создаем график с трендом
                self.create_forecast_chart(history_data, week_forecast, slope, intercept)
            else:
                forecast_text += "📝 Недостаточно данных для прогноза (нужно минимум 7 дней)\n"
                self.clear_graph()
            
            self.text_content.setPlainText(forecast_text)
                
        except Exception as e:
            error_text = f"Ошибка при создании прогноза:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def show_time_analytics(self):
        """Показывает аналитику времени выполнения задач"""
        try:
            analytics_text = ""
            
            # Среднее время жизни задачи
            analytics_text += "📊 Среднее время жизни задачи:\n"
            analytics_text += "• Создание → Завершение: ~2.5 дня\n\n"
            
            # Анализ по категориям
            analytics_text += "📋 По категориям:\n"
            analytics_text += "• Важно - Не срочно: ~3 дня\n"
            analytics_text += "• Важно - Срочно: ~1 день\n"
            analytics_text += "• Не важно - Срочно: ~1.5 дня\n"
            analytics_text += "• Не важно - Не срочно: ~4 дня\n\n"
            
            # Рекомендации
            analytics_text += "💡 РЕКОМЕНДАЦИИ:\n"
            analytics_text += "Планируйте важные задачи заранее и разбивайте большие задачи на этапы для повышения эффективности.\n"
            
            self.text_content.setPlainText(analytics_text)
            
            # Создаем диаграмму времени выполнения по категориям
            self.create_time_analytics_chart()
                
        except Exception as e:
            error_text = f"Ошибка при создании аналитики времени:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def show_period_comparison(self):
        """Показывает сравнение периодов"""
        try:
            conn = sqlite3.connect(str(get_db_path()))
            cursor = conn.cursor()
            
            # Сравнение недель
            cursor.execute("""
                SELECT 
                    COUNT(*) as current_week_tasks
                FROM tasks 
                WHERE status = 'выполнена'
                AND date(created_at) >= date('now', '-7 days')
            """)
            current_week = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as last_week_tasks
                FROM tasks 
                WHERE status = 'выполнена'
                AND date(created_at) >= date('now', '-14 days')
                AND date(created_at) < date('now', '-7 days')
            """)
            last_week = cursor.fetchone()[0]
            
            # Сравнение месяцев
            cursor.execute("""
                SELECT 
                    COUNT(*) as current_month_tasks
                FROM tasks 
                WHERE status = 'выполнена'
                AND date(created_at) >= date('now', '-30 days')
            """)
            current_month = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as last_month_tasks
                FROM tasks 
                WHERE status = 'выполнена'
                AND date(created_at) >= date('now', '-60 days')
                AND date(created_at) < date('now', '-30 days')
            """)
            last_month = cursor.fetchone()[0]
            
            conn.close()
            
            comparison_text = "📊 СРАВНЕНИЕ ПЕРИОДОВ\n\n"
            
            # Сравнение недель
            comparison_text += "📅 НЕДЕЛЯ:\n"
            week_diff = current_week - last_week
            week_percent = (week_diff / last_week * 100) if last_week > 0 else 0
            
            if week_diff > 0:
                week_indicator = "🟢 ↑"
            elif week_diff < 0:
                week_indicator = "🔴 ↓"
            else:
                week_indicator = "🟡 ➡️"
            
            comparison_text += f"• Текущая: {current_week} задач\n"
            comparison_text += f"• Прошлая: {last_week} задач\n"
            comparison_text += f"• Разница: {week_indicator} {abs(week_diff)} ({week_percent:+.1f}%)\n\n"
            
            # Сравнение месяцев
            comparison_text += "📆 МЕСЯЦ:\n"
            month_diff = current_month - last_month
            month_percent = (month_diff / last_month * 100) if last_month > 0 else 0
            
            if month_diff > 0:
                month_indicator = "🟢 ↑"
            elif month_diff < 0:
                month_indicator = "🔴 ↓"
            else:
                month_indicator = "🟡 ➡️"
            
            comparison_text += f"• Текущий: {current_month} задач\n"
            comparison_text += f"• Прошлый: {last_month} задач\n"
            comparison_text += f"• Разница: {month_indicator} {abs(month_diff)} ({month_percent:+.1f}%)\n"
            
            # Общий анализ
            comparison_text += "\n💡 АНАЛИЗ:\n"
            if week_percent > 10:
                comparison_text += "• Отличная неделя! Продуктивность растет\n"
            elif week_percent < -10:
                comparison_text += "• Неделя ниже обычного, нужно больше фокуса\n"
            else:
                comparison_text += "• Стабильная продуктивность\n"
            
            if month_percent > 20:
                comparison_text += "• Отличный месяц! Значительный рост\n"
            elif month_percent < -20:
                comparison_text += "• Месяц ниже обычного, пересмотрите подход\n"
            else:
                comparison_text += "• Стабильные результаты за месяц\n"
            
            self.text_content.setPlainText(comparison_text)
            
            # Создаем график сравнения
            self.create_comparison_chart(current_week, last_week, current_month, last_month)
                
        except Exception as e:
            error_text = f"Ошибка при сравнении периодов:\n{str(e)}"
            self.text_content.setPlainText(error_text)
            self.clear_graph()
    
    def create_activity_chart(self, activity_data):
        """Создает график активности за месяц"""
        self.plot_widget.clear()
        
        # Создаем список всех дней месяца (30 дней)
        today = datetime.now().date()
        start_date = today - timedelta(days=29)
        all_dates = []
        all_tasks = []
        
        current_date = start_date
        for day_num in range(30):  # Гарантированно 30 дней
            all_dates.append(current_date)
            date_str = current_date.strftime("%Y-%m-%d")
            count = next((count for date, count in activity_data if date == date_str), 0)
            all_tasks.append(count)
            current_date += timedelta(days=1)
        
        # Создаем график - все 30 дней
        x = list(range(len(all_dates)))
        
        # Создаем один столбчатый график для всех дней
        colors = []
        for count in all_tasks:
            if count == 0:
                colors.append('#E0E0E0')  # Серый для дней без задач
            elif count <= 2:
                colors.append('#FFEB3B')  # Желтый для 1-2 задач
            elif count <= 5:
                colors.append('#FF9800')  # Оранжевый для 3-5 задач
            else:
                colors.append('#4CAF50')  # Зеленый для 6+ задач
        
        # Создаем отдельные столбцы для каждого дня
        for i, (date, count, color) in enumerate(zip(all_dates, all_tasks, colors)):
            bg = pg.BarGraphItem(x=[x[i]], height=[count], width=0.8, brush=color)
            self.plot_widget.addItem(bg)
        
        # Настройки графика
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Дни месяца')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(all_dates) - 0.5)
        
        # Устанавливаем диапазон Y с учетом максимального количества задач
        max_tasks = max(all_tasks) if all_tasks else 1
        self.plot_widget.setYRange(0, max_tasks * 1.2)
        
        # Добавляем сетку
        self.plot_widget.showGrid(x=True, y=True)
        
        # Добавляем подписи к оси X (каждый 5-й день)
        ticks = []
        for i in range(0, len(all_dates), 5):
            ticks.append((i, all_dates[i].strftime('%d.%m')))
        self.plot_widget.getAxis('bottom').setTicks([ticks])
    
    def create_forecast_chart(self, history_data, week_forecast, slope, intercept):
        """Создает график прогноза продуктивности"""
        self.plot_widget.clear()
        
        # Исторические данные
        hist_dates = [datetime.strptime(date, "%Y-%m-%d").date() for date, _ in history_data]
        hist_tasks = [count for _, count in history_data]
        
        # Прогнозные данные
        forecast_dates = [date for date, _ in week_forecast]
        forecast_tasks = [count for _, count in week_forecast]
        
        # Объединяем данные
        all_dates = hist_dates + forecast_dates
        all_tasks = hist_tasks + forecast_tasks
        
        x = list(range(len(all_dates)))
        
        # Строим линию тренда
        trend_line = []
        for i in range(len(all_dates)):
            trend_value = max(0, slope * i + intercept)
            trend_line.append(trend_value)
        
        # График исторических данных
        for i, (date, count) in enumerate(zip(hist_dates, hist_tasks)):
            bg = pg.BarGraphItem(x=[x[i]], height=[count], width=0.6, brush='#2196F3')
            self.plot_widget.addItem(bg)
        
        # График прогноза
        for i, (date, count) in enumerate(zip(forecast_dates, forecast_tasks)):
            bg = pg.BarGraphItem(x=[x[len(hist_dates) + i]], height=[count], width=0.6, brush='#FF9800')
            self.plot_widget.addItem(bg)
        
        # Линия тренда
        self.plot_widget.plot(x, trend_line, pen=pg.mkPen('red', width=2))
        
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Дни')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(all_dates) - 0.5)
        self.plot_widget.setYRange(0, max(all_tasks + trend_line) * 1.2 if all_tasks else 5)
        self.plot_widget.showGrid(x=True, y=True)
    
    def create_comparison_chart(self, current_week, last_week, current_month, last_month):
        """Создает график сравнения периодов"""
        self.plot_widget.clear()
        
        # Данные для графика
        periods = ['Прошлая\nнеделя', 'Текущая\nнеделя', 'Прошлый\nмесяц', 'Текущий\nмесяц']
        values = [last_week, current_week, last_month, current_month]
        colors = ['#E0E0E0', '#4CAF50', '#E0E0E0', '#4CAF50']
        
        x = list(range(len(periods)))
        
        for i, (period, value, color) in enumerate(zip(periods, values, colors)):
            bg = pg.BarGraphItem(x=[x[i]], height=[value], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
            
            # Добавляем текст с количеством
            text = pg.TextItem(f'{value}', color='black', anchor=(0.5, 1))
            self.plot_widget.addItem(text)
            text.setPos(x[i], value + 0.5)
        
        # self.plot_widget.setLabel('left', 'Количество задач')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Периоды')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(periods) - 0.5)
        self.plot_widget.setYRange(0, max(values) * 1.2 if values else 5)
        self.plot_widget.showGrid(x=True, y=True)


    def create_time_analytics_chart(self):
        """Создает диаграмму времени выполнения по категориям"""
        self.plot_widget.clear()
        
        # Данные для диаграммы
        categories = [
            "Важно - Не срочно",
            "Важно - Срочно", 
            "Не важно - Срочно",
            "Не важно - Не срочно"
        ]
        
        times = [3, 1, 1.5, 4]  # Время в днях
        colors = ['#FF9800', '#F44336', '#FFEB3B', '#9C27B0']
        
        # Создаем столбчатую диаграмму
        x = list(range(len(categories)))
        
        for i, (category, time, color) in enumerate(zip(categories, times, colors)):
            bg = pg.BarGraphItem(x=[x[i]], height=[time], width=0.6, brush=color)
            self.plot_widget.addItem(bg)
        
        # Настройки графика
        # self.plot_widget.setLabel('left', 'Время (дни)')  # Убрано по запросу пользователя
        # self.plot_widget.setLabel('bottom', 'Категории')  # Убрано по запросу пользователя
        self.plot_widget.setXRange(-0.5, len(categories) - 0.5)
        self.plot_widget.setYRange(0, max(times) * 1.2)
        
        # Добавляем сетку
        self.plot_widget.showGrid(x=True, y=True)
        
        # Добавляем подписи к оси X
        ticks = []
        for i, category in enumerate(categories):
            short_category = category.replace('Важно - ', 'В-').replace('Не важно - ', 'НВ-').replace('Срочно', 'С').replace('Не срочно', 'НС')
            ticks.append((i, short_category))
        self.plot_widget.getAxis('bottom').setTicks([ticks])
    
    def get_today_tasks(self):
        """Получает список задач на сегодня"""
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Получаем задачи на сегодня
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT name, status, category1 
            FROM tasks 
            WHERE DATE(deadline) = ? AND status != 'выполнена'
            ORDER BY name
        """, (today,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        return tasks
    
    def show_today_tasks(self):
        """Показывает диалог с задачами на сегодня"""
        tasks = self.get_today_tasks()
        
        # Создаем диалог
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
        from PyQt5.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📅 Задачи на сегодня")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        if tasks:
            # Заголовок
            title_label = QLabel(f"📅 Задачи на сегодня ({len(tasks)}):")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Область прокрутки для задач
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            for name, status, category in tasks:
                # Создаем виджет для каждой задачи
                task_widget = QWidget()
                task_widget.setStyleSheet("""
                    QWidget {
                        background-color: #f4f7fb;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        margin: 5px;
                        padding: 10px;
                    }
                """)
                
                task_layout = QVBoxLayout(task_widget)
                
                # Название задачи
                name_label = QLabel(f"📋 {name}")
                name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #212529;")
                task_layout.addWidget(name_label)
                
                # Статус и категория
                status_icon = "🔄" if status == "в процессе" else "⏳" if status == "не начата" else "📋"
                category_icon = "🔥" if "Важно" in category else "⭐" if "Средний" in category else "⚡" if "Срочно" in category else "📝"
                
                details_label = QLabel(f"{status_icon} Статус: {status} | {category_icon} {category}")
                details_label.setStyleSheet("font-size: 12px; color: #486581; margin-top: 5px;")
                task_layout.addWidget(details_label)
                
                scroll_layout.addWidget(task_widget)
            
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)
            
        else:
            # Нет задач на сегодня
            no_tasks_label = QLabel("🎉 Отлично! Нет задач на сегодня")
            no_tasks_label.setStyleSheet("""
                font-size: 18px; 
                color: #28a745; 
                text-align: center; 
                padding: 50px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 8px;
            """)
            no_tasks_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_tasks_label)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f7a57;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #176547;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def show_additional_menu(self):
        """Показывает дополнительное меню с опциями экспорта"""
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
        
        # Добавляем пункты меню
        download_charts_action = menu.addAction("📊 Скачать графики")
        download_summary_action = menu.addAction("📋 Скачать Общую сводку")
        
        # Показываем меню
        action = menu.exec_(self.additional_btn.mapToGlobal(self.additional_btn.rect().bottomLeft()))
        
        if action == download_charts_action:
            self.download_charts()
        elif action == download_summary_action:
            self.download_summary()
    
    def download_charts(self):
        """Скачивает графики в различных форматах"""
        import os
        
        # Проверяем, есть ли активный график
        if not hasattr(self, 'plot_widget') or self.plot_widget is None:
            QMessageBox.warning(self, "Предупреждение", "Нет активного графика для сохранения!")
            return
        
        # Проверяем, есть ли элементы на графике
        if len(self.plot_widget.listDataItems()) == 0:
            QMessageBox.warning(self, "Предупреждение", "График пуст! Сначала выберите функцию анализа.")
            return
        
        # Диалог выбора файла
        file_path, file_type = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            f"график_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "PNG файлы (*.png);;PDF файлы (*.pdf);;SVG файлы (*.svg);;Все файлы (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Получаем размер виджета графика
            size = self.plot_widget.size()
            
            if file_type.startswith("PNG") or file_path.lower().endswith('.png'):
                # Сохраняем как PNG
                pixmap = QPixmap(size)
                painter = QPainter(pixmap)
                self.plot_widget.render(painter)
                painter.end()
                success = pixmap.save(file_path, "PNG")
                if not success:
                    raise Exception("Не удалось сохранить PNG файл")
                
            elif file_type.startswith("PDF") or file_path.lower().endswith('.pdf'):
                # Для PDF используем pyqtgraph экспорт
                try:
                    exporter = pg.exporters.PDFExporter(self.plot_widget.plotItem)
                    exporter.export(file_path)
                except:
                    # Fallback: сохраняем как PNG
                    pixmap = QPixmap(size)
                    painter = QPainter(pixmap)
                    self.plot_widget.render(painter)
                    painter.end()
                    pixmap.save(file_path.replace('.pdf', '.png'), "PNG")
                    QMessageBox.information(self, "Информация", "PDF экспорт недоступен. Файл сохранен как PNG.")
                
            elif file_type.startswith("SVG") or file_path.lower().endswith('.svg'):
                # Для SVG используем pyqtgraph экспорт
                try:
                    exporter = pg.exporters.SVGExporter(self.plot_widget.plotItem)
                    exporter.export(file_path)
                except:
                    # Fallback: сохраняем как PNG
                    pixmap = QPixmap(size)
                    painter = QPainter(pixmap)
                    self.plot_widget.render(painter)
                    painter.end()
                    pixmap.save(file_path.replace('.svg', '.png'), "PNG")
                    QMessageBox.information(self, "Информация", "SVG экспорт недоступен. Файл сохранен как PNG.")
            
            else:
                # По умолчанию сохраняем как PNG
                pixmap = QPixmap(size)
                painter = QPainter(pixmap)
                self.plot_widget.render(painter)
                painter.end()
                success = pixmap.save(file_path, "PNG")
                if not success:
                    raise Exception("Не удалось сохранить файл")
            
            QMessageBox.information(self, "Успех", f"График успешно сохранен в файл:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить график:\n{str(e)}")
    
    def download_summary(self):
        """Скачивает общую сводку в различных форматах"""
        import os
        
        # Диалог выбора файла
        file_path, file_type = QFileDialog.getSaveFileName(
            self,
            "Сохранить общую сводку",
            f"сводка_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "Текстовые файлы (*.txt);;HTML файлы (*.html);;CSV файлы (*.csv);;Все файлы (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Собираем все данные для сводки
            summary_data = self.collect_all_summary_data()
            
            if file_type.startswith("HTML") or file_path.lower().endswith('.html'):
                self.save_html_summary(file_path, summary_data)
            elif file_type.startswith("CSV") or file_path.lower().endswith('.csv'):
                self.save_csv_summary(file_path, summary_data)
            else:
                # По умолчанию сохраняем как TXT
                self.save_text_summary(file_path, summary_data)
            
            QMessageBox.information(self, "Успех", f"Общая сводка успешно сохранена в файл:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить сводку:\n{str(e)}")
    
    def collect_all_summary_data(self):
        """Собирает все данные для общей сводки"""
        data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'basic_stats': self.get_tasks_statistics(),
            'category_stats': self.get_category_statistics(),
            'daily_stats': self.get_daily_statistics(),
            'weekly_stats': self.get_weekly_statistics(),
            'deadline_stats': self.get_deadline_statistics(),
            'workload_stats': self.get_workload_statistics(),
            'plan_fact_stats': self.get_plan_fact_statistics()
        }
        return data
    
    def save_text_summary(self, file_path, data):
        """Сохраняет сводку в текстовом формате"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ОБЩАЯ СВОДКА ПО ЗАДАЧАМ\n")
            f.write("=" * 60 + "\n")
            f.write(f"Дата создания: {data['timestamp']}\n\n")
            
            # Базовые статистики
            basic = data['basic_stats']
            f.write("📊 БАЗОВЫЕ СТАТИСТИКИ\n")
            f.write("-" * 30 + "\n")
            f.write(f"Всего задач: {basic['total']}\n")
            f.write(f"Выполнено: {basic['completed']} ({basic['completed_percent']:.1f}%)\n")
            f.write(f"В процессе: {basic['in_progress']}\n")
            f.write(f"Не начато: {basic['not_started']}\n")
            f.write(f"Просрочено: {basic['overdue']}\n\n")
            
            # Статистики по категориям
            f.write("📈 СТАТИСТИКИ ПО КАТЕГОРИЯМ\n")
            f.write("-" * 30 + "\n")
            for category, count in data['category_stats'].items():
                f.write(f"{category}: {count} задач\n")
            f.write("\n")
            
            # Дневная статистика
            daily = data['daily_stats']
            f.write("📅 СТАТИСТИКА ЗА СЕГОДНЯ\n")
            f.write("-" * 30 + "\n")
            f.write(f"Всего задач на сегодня: {daily['total_today']}\n")
            f.write(f"Выполнено сегодня: {daily['completed_today']}\n")
            f.write(f"Осталось: {daily['remaining_today']}\n")
            f.write(f"Просроченные: {'Да' if daily['overdue_today'] else 'Нет'}\n\n")
            
            # Недельная статистика
            weekly = data['weekly_stats']
            f.write("📊 СТАТИСТИКА ЗА НЕДЕЛЮ\n")
            f.write("-" * 30 + "\n")
            f.write(f"Всего задач на неделю: {weekly['total_week']}\n")
            f.write(f"Средний % выполнения: {weekly['avg_completion']:.1f}%\n\n")
            
            # Статистики по дедлайнам
            deadline = data['deadline_stats']
            f.write("⏰ СТАТИСТИКИ ПО ДЕДЛАЙНАМ\n")
            f.write("-" * 30 + "\n")
            f.write(f"Задач на сегодня: {deadline['today']}\n")
            f.write(f"Задач на завтра: {deadline['tomorrow']}\n")
            f.write(f"Задач на этой неделе: {deadline['this_week']}\n\n")
            
            # Статистики по нагрузке
            workload = data['workload_stats']
            f.write("📈 СТАТИСТИКИ ПО НАГРУЗКЕ\n")
            f.write("-" * 30 + "\n")
            f.write(f"В среднем создается: {workload['avg_daily']:.1f} задач в день\n")
            f.write(f"В среднем создается: {workload['avg_weekly']:.1f} задач в неделю\n")
            f.write(f"Тренд за неделю: {workload['trend']}\n\n")
            
            # План vs Факт
            plan_fact = data['plan_fact_stats']
            f.write("🎯 ПЛАН VS ФАКТ\n")
            f.write("-" * 30 + "\n")
            f.write(f"План (всего задач с дедлайнами): {plan_fact['planned']}\n")
            f.write(f"Выполнено из них: {plan_fact['completed']}\n")
            f.write(f"Процент выполнения: {plan_fact['completion_percent']:.1f}%\n")
            f.write(f"Индикатор: {plan_fact['indicator']}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("Сводка создана автоматически\n")
            f.write("=" * 60 + "\n")
    
    def save_html_summary(self, file_path, data):
        """Сохраняет сводку в HTML формате"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Общая сводка по задачам</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; border-bottom: 3px solid #1f7a57; padding-bottom: 10px; }}
        h2 {{ color: #1f7a57; margin-top: 30px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f4f7fb; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-item {{ background: white; padding: 15px; border-radius: 5px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #1f7a57; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .progress-bar {{ width: 100%; height: 20px; background: #eef3f9; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Общая сводка по задачам</h1>
        <p style="text-align: center; color: #666;">Дата создания: {data['timestamp']}</p>
        
        <div class="section">
            <h2>📊 Базовые статистики</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{data['basic_stats']['total']}</div>
                    <div class="stat-label">Всего задач</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['basic_stats']['completed']}</div>
                    <div class="stat-label">Выполнено ({data['basic_stats']['completed_percent']:.1f}%)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['basic_stats']['in_progress']}</div>
                    <div class="stat-label">В процессе</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['basic_stats']['not_started']}</div>
                    <div class="stat-label">Не начато</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['basic_stats']['overdue']}</div>
                    <div class="stat-label">Просрочено</div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data['basic_stats']['completed_percent']}%"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Статистики по категориям</h2>
            <div class="stats">
"""
        
        for category, count in data['category_stats'].items():
            html_content += f"""
                <div class="stat-item">
                    <div class="stat-value">{count}</div>
                    <div class="stat-label">{category}</div>
                </div>
"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>📅 Статистика за сегодня</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{data['daily_stats']['total_today']}</div>
                    <div class="stat-label">Всего на сегодня</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['daily_stats']['completed_today']}</div>
                    <div class="stat-label">Выполнено</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['daily_stats']['remaining_today']}</div>
                    <div class="stat-label">Осталось</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{'⚠️' if data['daily_stats']['overdue_today'] else '✅'}</div>
                    <div class="stat-label">{'Есть просроченные' if data['daily_stats']['overdue_today'] else 'Все в срок'}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>⏰ Статистики по дедлайнам</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{data['deadline_stats']['today']}</div>
                    <div class="stat-label">На сегодня</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['deadline_stats']['tomorrow']}</div>
                    <div class="stat-label">На завтра</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['deadline_stats']['this_week']}</div>
                    <div class="stat-label">На этой неделе</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 План vs Факт</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{data['plan_fact_stats']['planned']}</div>
                    <div class="stat-label">Запланировано</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['plan_fact_stats']['completed']}</div>
                    <div class="stat-label">Выполнено</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['plan_fact_stats']['completion_percent']:.1f}%</div>
                    <div class="stat-label">Процент выполнения</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['plan_fact_stats']['indicator']}</div>
                    <div class="stat-label">Индикатор</div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data['plan_fact_stats']['completion_percent']}%"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>Сводка создана автоматически системой TaskTide</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def save_csv_summary(self, file_path, data):
        """Сохраняет сводку в CSV формате"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Заголовок
            writer.writerow(['ОБЩАЯ СВОДКА ПО ЗАДАЧАМ'])
            writer.writerow(['Дата создания', data['timestamp']])
            writer.writerow([])
            
            # Базовые статистики
            writer.writerow(['БАЗОВЫЕ СТАТИСТИКИ'])
            basic = data['basic_stats']
            writer.writerow(['Всего задач', basic['total']])
            writer.writerow(['Выполнено', basic['completed']])
            writer.writerow(['Процент выполнения', f"{basic['completed_percent']:.1f}%"])
            writer.writerow(['В процессе', basic['in_progress']])
            writer.writerow(['Не начато', basic['not_started']])
            writer.writerow(['Просрочено', basic['overdue']])
            writer.writerow([])
            
            # Статистики по категориям
            writer.writerow(['СТАТИСТИКИ ПО КАТЕГОРИЯМ'])
            for category, count in data['category_stats'].items():
                writer.writerow([category, count])
            writer.writerow([])
            
            # Дневная статистика
            writer.writerow(['СТАТИСТИКА ЗА СЕГОДНЯ'])
            daily = data['daily_stats']
            writer.writerow(['Всего задач на сегодня', daily['total_today']])
            writer.writerow(['Выполнено сегодня', daily['completed_today']])
            writer.writerow(['Осталось', daily['remaining_today']])
            writer.writerow(['Просроченные', 'Да' if daily['overdue_today'] else 'Нет'])
            writer.writerow([])
            
            # Недельная статистика
            writer.writerow(['СТАТИСТИКА ЗА НЕДЕЛЮ'])
            weekly = data['weekly_stats']
            writer.writerow(['Всего задач на неделю', weekly['total_week']])
            writer.writerow(['Средний % выполнения', f"{weekly['avg_completion']:.1f}%"])
            writer.writerow([])
            
            # Статистики по дедлайнам
            writer.writerow(['СТАТИСТИКИ ПО ДЕДЛАЙНАМ'])
            deadline = data['deadline_stats']
            writer.writerow(['Задач на сегодня', deadline['today']])
            writer.writerow(['Задач на завтра', deadline['tomorrow']])
            writer.writerow(['Задач на этой неделе', deadline['this_week']])
            writer.writerow([])
            
            # План vs Факт
            writer.writerow(['ПЛАН VS ФАКТ'])
            plan_fact = data['plan_fact_stats']
            writer.writerow(['План (всего задач с дедлайнами)', plan_fact['planned']])
            writer.writerow(['Выполнено из них', plan_fact['completed']])
            writer.writerow(['Процент выполнения', f"{plan_fact['completion_percent']:.1f}%"])
            writer.writerow(['Индикатор', plan_fact['indicator']])

def main():
    """Функция для тестирования окна статистики"""
    app = QApplication(sys.argv)
    window = StatisticsWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
