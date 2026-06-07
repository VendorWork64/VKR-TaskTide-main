# notes_db.py - Функции для работы с заметками

import sqlite3
from src.tasktide.paths import get_db_path
from datetime import datetime

def add_note(title, content, category="📝 Общие заметки", task_id=None, tags="", parent_note_id=None):
    """Добавляет новую заметку в базу данных"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notes (title, content, category, task_id, tags, parent_note_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, content, category, task_id, tags, parent_note_id))
    conn.commit()
    conn.close()

def get_all_notes():
    """Получает все заметки 1-го уровня из базы данных"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, t.name as task_name 
        FROM notes n 
        LEFT JOIN tasks t ON n.task_id = t.id 
        WHERE n.parent_note_id IS NULL
        ORDER BY n.is_pinned DESC, n.updated_at DESC
    """)
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    """Получает заметку по ID"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note

def update_note(note_id, title, content, category, tags=""):
    """Обновляет заметку"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE notes SET title = ?, content = ?, category = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (title, content, category, tags, note_id))
    conn.commit()
    conn.close()

def delete_note(note_id):
    """Удаляет заметку"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

def search_notes(search_text, category_filter="Все категории"):
    """Поиск заметок по тексту и категории"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    query = """
        SELECT n.*, t.name as task_name 
        FROM notes n 
        LEFT JOIN tasks t ON n.task_id = t.id 
        WHERE (n.title LIKE ? OR n.content LIKE ? OR n.tags LIKE ?)
    """
    params = [f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"]
    
    if category_filter != "Все категории":
        query += " AND n.category = ?"
        params.append(category_filter)
    
    query += " ORDER BY n.is_pinned DESC, n.updated_at DESC"
    
    cursor.execute(query, params)
    notes = cursor.fetchall()
    conn.close()
    return notes

def pin_note(note_id, is_pinned=True):
    """Закрепляет/открепляет заметку"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET is_pinned = ? WHERE id = ?", (is_pinned, note_id))
    conn.commit()
    conn.close()

def get_notes_by_task(task_id):
    """Получает все заметки 1-го уровня, связанные с задачей (без parent_note_id)"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE task_id = ? AND parent_note_id IS NULL ORDER BY created_at DESC", (task_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_notes_by_parent(parent_note_id):
    """Получает все подзадачи для конкретной заметки"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, t.name as task_name 
        FROM notes n 
        LEFT JOIN tasks t ON n.task_id = t.id 
        WHERE n.parent_note_id = ?
        ORDER BY n.is_pinned DESC, n.updated_at DESC
    """, (parent_note_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_hierarchy(note_id):
    """Получает иерархию заметки (родительские заметки)"""
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    
    hierarchy = []
    current_id = note_id
    
    while current_id:
        cursor.execute("""
            SELECT n.*, t.name as task_name, n.parent_note_id
            FROM notes n 
            LEFT JOIN tasks t ON n.task_id = t.id 
            WHERE n.id = ?
        """, (current_id,))
        
        note = cursor.fetchone()
        if note:
            hierarchy.insert(0, note)
            current_id = note[7]  # parent_note_id
        else:
            break
    
    conn.close()
    return hierarchy
