import json
import sqlite3
from src.tasktide.paths import get_db_path
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.tasktide.database import (
    add_focus_session,
    add_task,
    clear_focus_sessions,
    delete_task,
    get_all_tasks,
    get_focus_daily_stats,
    get_tasks_approaching_deadline,
    get_tasks_statistics,
    init_db,
    update_focus_daily_stats,
    update_task_status,
)
from src.tasktide.notes_db import add_note, delete_note, pin_note, update_note

HOST = "127.0.0.1"
PORT = 8765


def map_task(row):
    deadline_raw = row[4] or ""
    deadline_label = deadline_raw
    try:
        deadline_dt = datetime.fromisoformat(deadline_raw)
        deadline_label = deadline_dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        pass

    return {
        "id": row[0],
        "name": row[1],
        "priority": row[2],
        "category": row[3],
        "deadline": deadline_label,
        "status": row[5],
        "description": row[6] or "",
        "created_at": row[7],
        "updated_at": row[8],
    }


def map_note(row):
    return {
        "id": row[0],
        "task_id": row[1],
        "parent_note_id": row[2],
        "title": row[3],
        "content": row[4] or "",
        "category": row[5] or "📝 Общие заметки",
        "tags": row[6] or "",
        "is_pinned": bool(row[7]),
        "created_at": row[8],
        "updated_at": row[9],
        "task_name": row[10] if len(row) > 10 else None,
    }


def get_notes_by_task(task_id):
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            n.id,
            n.task_id,
            n.parent_note_id,
            n.title,
            n.content,
            n.category,
            n.tags,
            n.is_pinned,
            n.created_at,
            n.updated_at,
            t.name as task_name
        FROM notes n
        LEFT JOIN tasks t ON n.task_id = t.id
        WHERE n.task_id = ?
        ORDER BY n.is_pinned DESC, n.updated_at DESC
        """,
        (task_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_notes_flat():
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            n.id,
            n.task_id,
            n.parent_note_id,
            n.title,
            n.content,
            n.category,
            n.tags,
            n.is_pinned,
            n.created_at,
            n.updated_at,
            t.name as task_name
        FROM notes n
        LEFT JOIN tasks t ON n.task_id = t.id
        ORDER BY
            CASE WHEN n.parent_note_id IS NULL THEN 0 ELSE 1 END,
            n.parent_note_id ASC,
            n.is_pinned DESC,
            n.updated_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recent_focus_sessions(limit=20):
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT fs.id, fs.task_id, fs.duration_minutes, fs.session_type, fs.created_at, t.name
        FROM focus_sessions fs
        LEFT JOIN tasks t ON fs.task_id = t.id
        ORDER BY fs.created_at DESC, fs.id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "task_id": row[1],
            "duration_minutes": row[2],
            "session_type": row[3],
            "created_at": row[4],
            "task_name": row[5],
        }
        for row in rows
    ]


class TaskApiHandler(BaseHTTPRequestHandler):
    server_version = "TaskTideApi/2.0"

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, payload, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/health":
            self._send_json({"ok": True})
            return

        if path == "/api/overview":
            stats = get_tasks_statistics()
            tasks = [map_task(row) for row in get_all_tasks()][:6]
            focus = get_focus_daily_stats()
            self._send_json(
                {"stats": stats, "focus": focus, "recent_tasks": tasks, "server_time": datetime.now().isoformat()}
            )
            return

        if path == "/api/tasks":
            tasks = [map_task(row) for row in get_all_tasks()]
            self._send_json({"items": tasks})
            return

        if path == "/api/stats":
            self._send_json(get_tasks_statistics())
            return

        if path == "/api/deadlines/approaching":
            self._send_json({"items": get_tasks_approaching_deadline()})
            return

        if path == "/api/notes":
            task_id_values = query.get("task_id", [])
            if task_id_values:
                try:
                    task_id = int(task_id_values[0])
                except ValueError:
                    self._send_json({"error": "Invalid task_id"}, status=400)
                    return
                rows = get_notes_by_task(task_id)
            else:
                rows = get_all_notes_flat()
            self._send_json({"items": [map_note(row) for row in rows]})
            return

        if path == "/api/focus/stats":
            self._send_json(get_focus_daily_stats())
            return

        if path == "/api/focus/sessions":
            limit = 20
            if query.get("limit"):
                try:
                    limit = max(1, min(10000, int(query["limit"][0])))
                except ValueError:
                    pass
            self._send_json({"items": get_recent_focus_sessions(limit)})
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/tasks":
            try:
                payload = self._read_json_body()
                name = str(payload.get("name", "")).strip()
                if not name:
                    self._send_json({"error": "Task name is required"}, status=400)
                    return

                category1 = str(payload.get("priority", "Важно - Срочно")).strip()
                category2 = str(payload.get("category", "Работа")).strip()
                description = str(payload.get("description", "")).strip()
                deadline_mode = str(payload.get("deadline_mode", "")).strip().lower()
                deadline_at_raw = payload.get("deadline_at")
                if deadline_mode == "absolute" or deadline_at_raw is not None:
                    deadline_at = str(deadline_at_raw or "").strip()
                    if not deadline_at:
                        self._send_json({"error": "Deadline date is required"}, status=400)
                        return
                    try:
                        deadline = datetime.fromisoformat(deadline_at)
                    except ValueError:
                        self._send_json({"error": "Invalid deadline_at format. Use ISO datetime"}, status=400)
                        return
                    if deadline <= datetime.now():
                        self._send_json({"error": "Deadline must be in the future"}, status=400)
                        return
                else:
                    duration_raw = payload.get("duration")
                    if duration_raw is not None:
                        duration_match = str(duration_raw).strip().replace(" ", "").split(":")
                        if len(duration_match) != 3 or not (
                            len(duration_match[0]) == 3
                            and len(duration_match[1]) == 2
                            and len(duration_match[2]) == 2
                            and all(part.isdigit() for part in duration_match)
                        ):
                            self._send_json({"error": "Invalid duration format. Use 000:00:00 (days:hours:minutes)"}, status=400)
                            return
                        try:
                            d_days = max(0, int(duration_match[0]))
                            d_hours = max(0, int(duration_match[1]))
                            d_minutes = max(0, int(duration_match[2]))
                        except ValueError:
                            self._send_json({"error": "Invalid duration format. Use 000:00:00 (days:hours:minutes)"}, status=400)
                            return
                        minutes = d_minutes + d_hours * 60 + d_days * 24 * 60
                        if minutes <= 0:
                            self._send_json({"error": "Duration must be greater than 0"}, status=400)
                            return
                    else:
                        minutes = max(1, int(payload.get("minutes", 60)))
                    deadline = datetime.now() + timedelta(minutes=minutes)
                add_task(name, category1, category2, deadline.isoformat(timespec="seconds"), description)
                self._send_json({"ok": True}, status=201)
                return
            except (ValueError, json.JSONDecodeError):
                self._send_json({"error": "Invalid request body"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        if path == "/api/notes":
            try:
                payload = self._read_json_body()
                title = str(payload.get("title", "")).strip()
                if not title:
                    self._send_json({"error": "Note title is required"}, status=400)
                    return

                content = str(payload.get("content", "")).strip()
                task_id = payload.get("task_id")
                parent_note_id = payload.get("parent_note_id")
                category = str(payload.get("category", "📝 Общие заметки")).strip()
                tags = str(payload.get("tags", "")).strip()
                add_note(title, content, category, task_id, tags, parent_note_id)
                self._send_json({"ok": True}, status=201)
                return
            except (ValueError, json.JSONDecodeError):
                self._send_json({"error": "Invalid request body"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        if path == "/api/focus/session":
            try:
                payload = self._read_json_body()
                task_id = payload.get("task_id")
                session_type = str(payload.get("session_type", "pomodoro"))
                duration_minutes = max(1, int(payload.get("duration_minutes", 25)))
                notes = str(payload.get("notes", ""))

                add_focus_session(task_id=task_id, session_type=session_type, duration_minutes=duration_minutes, notes=notes)

                if session_type == "pomodoro":
                    update_focus_daily_stats(
                        focus_minutes=duration_minutes, completed_cycles=1, pomodoro_sessions=1
                    )
                elif session_type == "short_break":
                    update_focus_daily_stats(short_breaks=1)
                elif session_type == "long_break":
                    update_focus_daily_stats(long_breaks=1)

                self._send_json({"ok": True}, status=201)
                return
            except (ValueError, json.JSONDecodeError):
                self._send_json({"error": "Invalid request body"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        self._send_json({"error": "Not found"}, status=404)

    def do_PATCH(self):
        path = urlparse(self.path).path
        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        if path.startswith("/api/tasks/") and path.endswith("/status"):
            task_id_raw = path[len("/api/tasks/") : -len("/status")]
            try:
                task_id = int(task_id_raw)
                status = str(payload.get("status", "")).strip()
                if status not in {"не начата", "в процессе", "выполнена"}:
                    self._send_json({"error": "Invalid status"}, status=400)
                    return
                update_task_status(task_id, status)
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid request"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        if path.startswith("/api/notes/") and path.endswith("/pin"):
            note_id_raw = path[len("/api/notes/") : -len("/pin")]
            try:
                note_id = int(note_id_raw)
                is_pinned = bool(payload.get("is_pinned", True))
                pin_note(note_id, is_pinned)
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid note id"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        if path.startswith("/api/notes/"):
            note_id_raw = path[len("/api/notes/") :]
            try:
                note_id = int(note_id_raw)
                title = str(payload.get("title", "")).strip()
                if not title:
                    self._send_json({"error": "Note title is required"}, status=400)
                    return
                content = str(payload.get("content", "")).strip()
                category = str(payload.get("category", "📝 Общие заметки")).strip()
                tags = str(payload.get("tags", "")).strip()
                update_note(note_id, title, content, category, tags)
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid note id"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        self._send_json({"error": "Not found"}, status=404)

    def do_DELETE(self):
        path = urlparse(self.path).path

        if path == "/api/focus/sessions":
            try:
                clear_focus_sessions()
                self._send_json({"ok": True})
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        if path.startswith("/api/tasks/"):
            task_id_raw = path[len("/api/tasks/") :]
            try:
                task_id = int(task_id_raw)
                delete_task(task_id)
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid task id"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        if path.startswith("/api/notes/"):
            note_id_raw = path[len("/api/notes/") :]
            try:
                note_id = int(note_id_raw)
                delete_note(note_id)
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid note id"}, status=400)
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
                return

        self._send_json({"error": "Not found"}, status=404)

    def log_message(self, format_str, *args):
        return


def run():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), TaskApiHandler)
    print(f"TaskTide API listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
