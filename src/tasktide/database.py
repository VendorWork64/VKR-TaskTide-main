import sqlite3
from src.tasktide.paths import get_db_path
from datetime import datetime, timedelta

def init_db():
    # Подключение к базе данных (или создание, если она не существует)
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()

    # Создание таблицы задач
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category1 TEXT NOT NULL,
            category2 TEXT NOT NULL,
            deadline TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'не начата',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавляем столбцы created_at и updated_at если их нет
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except:
        pass  # Столбец уже существует
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except:
        pass  # Столбец уже существует

    # Создание таблицы истории
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_tasks INTEGER
        )
    ''')
    
    # Создание таблицы заметок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            parent_note_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT DEFAULT '📝 Общие заметки',
            tags TEXT,
            is_pinned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (parent_note_id) REFERENCES notes (id)
        )
    ''')
    
    # Добавляем колонку parent_note_id если её нет (для существующих баз данных)
    try:
        cursor.execute("ALTER TABLE notes ADD COLUMN parent_note_id INTEGER")
        cursor.execute("ALTER TABLE notes ADD CONSTRAINT fk_parent_note FOREIGN KEY (parent_note_id) REFERENCES notes (id)")
    except sqlite3.OperationalError:
        # Колонка уже существует или ограничение уже добавлено
        pass
    
    # Создание таблицы вложений к заметкам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_attachments (
            id INTEGER PRIMARY KEY,
            note_id INTEGER,
            file_path TEXT,
            file_type TEXT,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes (id)
        )
    ''')
    
    # Создание таблицы сессий фокуса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_minutes INTEGER,
            session_type TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
    ''')
    
    # Создание таблицы настроек фокуса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_settings (
            id INTEGER PRIMARY KEY,
            work_duration INTEGER DEFAULT 25,
            short_break INTEGER DEFAULT 5,
            long_break INTEGER DEFAULT 15,
            sessions_before_long_break INTEGER DEFAULT 4,
            sound_enabled BOOLEAN DEFAULT TRUE,
            auto_start_break BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы ежедневной статистики фокуса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_daily_stats (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            total_focus_minutes INTEGER DEFAULT 0,
            completed_cycles INTEGER DEFAULT 0,
            pomodoro_sessions INTEGER DEFAULT 0,
            short_breaks INTEGER DEFAULT 0,
            long_breaks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date)
        )
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

def add_task(name, category1, category2, deadline, description):
    """Добавляет новую задачу в базу данных"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (name, category1, category2, deadline, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (name, category1, category2, deadline, description))
    conn.commit()
    conn.close()

def get_all_tasks():
    """Получает все задачи из базы данных"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC, id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id):
    """Получает задачу по ID"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def update_task_status(task_id, status):
    """Обновляет статус задачи"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Удаляет задачу"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, name, category1, category2, deadline, description):
    """Обновляет данные задачи"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks SET name = ?, category1 = ?, category2 = ?, deadline = ?, description = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (name, category1, category2, deadline, description, task_id))
    conn.commit()
    conn.close()

def get_tasks_statistics():
    """Получает статистику по задачам"""
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
    
    conn.close()
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'in_progress': in_progress_tasks,
        'not_started': not_started_tasks
    }

def add_completed_task_to_history():
    """Добавляет запись о выполненной задаче в историю"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    # Получаем количество выполненных задач за сегодня
    today = datetime.now().date()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'выполнена' AND date(deadline) = ?", (today,))
    completed_today = cursor.fetchone()[0]
    
    # Проверяем, есть ли уже запись за сегодня
    cursor.execute("SELECT * FROM history WHERE date(date) = ?", (today,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Обновляем существующую запись
        cursor.execute("UPDATE history SET completed_tasks = ? WHERE date(date) = ?", (completed_today, today))
    else:
        # Создаем новую запись
        cursor.execute("INSERT INTO history (completed_tasks) VALUES (?)", (completed_today,))
    
    conn.commit()
    conn.close()

def get_tasks_approaching_deadline():
    """Получает задачи, приближающиеся к дедлайну"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # Определяем точные временные интервалы для уведомлений (от меньшего к большему)
    intervals = [
        (timedelta(minutes=1), "1 минута"),     # ровно 1 минута
        (timedelta(minutes=5), "5 минут"),      # ровно 5 минут
        (timedelta(minutes=10), "10 минут"),    # ровно 10 минут
        (timedelta(minutes=30), "30 минут"),    # ровно 30 минут
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
            
            # Проверяем каждый интервал на точное совпадение (с допуском в 2 минуты)
            tolerance = timedelta(minutes=2)  # Допуск в 2 минуты для точности
            
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

def get_focus_daily_stats(date=None):
    """Получает статистику фокуса за указанную дату (по умолчанию сегодня)"""
    if date is None:
        date = datetime.now().date()
    
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT total_focus_minutes, completed_cycles, pomodoro_sessions, short_breaks, long_breaks
        FROM focus_daily_stats 
        WHERE date = ?
    """, (date,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'total_focus_minutes': result[0],
            'completed_cycles': result[1],
            'pomodoro_sessions': result[2],
            'short_breaks': result[3],
            'long_breaks': result[4]
        }
    else:
        return {
            'total_focus_minutes': 0,
            'completed_cycles': 0,
            'pomodoro_sessions': 0,
            'short_breaks': 0,
            'long_breaks': 0
        }

def update_focus_daily_stats(focus_minutes=0, completed_cycles=0, pomodoro_sessions=0, short_breaks=0, long_breaks=0, date=None):
    """Обновляет статистику фокуса за указанную дату (по умолчанию сегодня)"""
    if date is None:
        date = datetime.now().date()
    
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже запись за эту дату
    cursor.execute("SELECT id FROM focus_daily_stats WHERE date = ?", (date,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Обновляем существующую запись
        cursor.execute("""
            UPDATE focus_daily_stats 
            SET total_focus_minutes = total_focus_minutes + ?,
                completed_cycles = completed_cycles + ?,
                pomodoro_sessions = pomodoro_sessions + ?,
                short_breaks = short_breaks + ?,
                long_breaks = long_breaks + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE date = ?
        """, (focus_minutes, completed_cycles, pomodoro_sessions, short_breaks, long_breaks, date))
    else:
        # Создаем новую запись
        cursor.execute("""
            INSERT INTO focus_daily_stats 
            (date, total_focus_minutes, completed_cycles, pomodoro_sessions, short_breaks, long_breaks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, focus_minutes, completed_cycles, pomodoro_sessions, short_breaks, long_breaks))
    
    conn.commit()
    conn.close()

def add_focus_session(task_id=None, session_type="pomodoro", duration_minutes=25, notes=""):
    """Добавляет запись о сессии фокуса"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO focus_sessions 
        (task_id, start_time, end_time, duration_minutes, session_type, notes)
        VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)
    """, (task_id, duration_minutes, session_type, notes))
    
    conn.commit()
    conn.close()

def clear_focus_sessions():
    """Удаляет все записи истории сессий фокуса."""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM focus_sessions")
    conn.commit()
    conn.close()
