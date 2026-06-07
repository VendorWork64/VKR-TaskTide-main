import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = os.getenv("TASKTIDE_HOST", "0.0.0.0")
PORT = int(os.getenv("TASKTIDE_PORT", "8765"))
DB_PATH = os.getenv("TASKTIDE_DB_PATH", os.path.join(os.path.dirname(__file__), "data", "tasktide_server.db"))
JWT_SECRET_FILE = os.getenv(
    "TASKTIDE_JWT_SECRET_FILE", os.path.join(os.path.dirname(__file__), "data", "jwt_secret.txt")
)
JWT_TTL_SECONDS = int(os.getenv("TASKTIDE_JWT_TTL_SECONDS", str(30 * 24 * 60 * 60)))


def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat()


def parse_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def load_jwt_secret():
    env_secret = str(os.getenv("TASKTIDE_JWT_SECRET", "")).strip()
    if env_secret:
        if len(env_secret) < 32:
            raise ValueError("TASKTIDE_JWT_SECRET must be at least 32 characters long")
        return env_secret

    ensure_parent_dir(JWT_SECRET_FILE)
    if os.path.exists(JWT_SECRET_FILE):
        with open(JWT_SECRET_FILE, "r", encoding="utf-8") as fh:
            file_secret = fh.read().strip()
        if len(file_secret) < 32:
            raise ValueError(f"JWT secret file is too short: {JWT_SECRET_FILE}")
        return file_secret

    generated = secrets.token_urlsafe(64)
    with open(JWT_SECRET_FILE, "w", encoding="utf-8") as fh:
        fh.write(generated)
    try:
        os.chmod(JWT_SECRET_FILE, 0o600)
    except OSError:
        pass
    return generated


JWT_SECRET = load_jwt_secret()


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    ensure_parent_dir(DB_PATH)
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'не начата',
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                parent_note_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT,
                tags TEXT,
                is_pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL,
                FOREIGN KEY(parent_note_id) REFERENCES notes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                duration_minutes INTEGER NOT NULL,
                session_type TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS focus_daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                total_focus_minutes INTEGER NOT NULL DEFAULT 0,
                completed_cycles INTEGER NOT NULL DEFAULT 0,
                pomodoro_sessions INTEGER NOT NULL DEFAULT 0,
                short_breaks INTEGER NOT NULL DEFAULT 0,
                long_breaks INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, date),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def b64url_encode(raw_bytes):
    return base64.urlsafe_b64encode(raw_bytes).rstrip(b"=").decode("ascii")


def b64url_decode(raw_str):
    padding = "=" * (-len(raw_str) % 4)
    return base64.urlsafe_b64decode((raw_str + padding).encode("ascii"))


def sign_jwt(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(JWT_SECRET.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{b64url_encode(signature)}"


def create_access_token(user_id):
    payload = {"uid": int(user_id), "exp": int(time.time()) + JWT_TTL_SECONDS}
    return sign_jwt(payload)


def verify_access_token(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        message = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_signature = hmac.new(JWT_SECRET.encode("utf-8"), message, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_signature, b64url_decode(signature_b64)):
            return None
        payload = json.loads(b64url_decode(payload_b64).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        uid = int(payload.get("uid", 0))
        return uid if uid > 0 else None
    except Exception:
        return None


def hash_password(password, salt_hex=None):
    if salt_hex is None:
        salt_hex = secrets.token_hex(16)
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt_hex, digest.hex()


def verify_password(password, salt_hex, expected_hash):
    _, computed = hash_password(password, salt_hex)
    return hmac.compare_digest(computed, expected_hash)


def task_row_to_json(row):
    deadline_raw = row["deadline"] or ""
    deadline_label = deadline_raw
    dt = parse_iso(deadline_raw)
    if dt:
        deadline_label = dt.strftime("%d.%m.%Y %H:%M")
    return {
        "id": row["id"],
        "name": row["name"],
        "priority": row["priority"],
        "category": row["category"],
        "deadline": deadline_label,
        "status": row["status"],
        "description": row["description"] or "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def note_row_to_json(row):
    return {
        "id": row["id"],
        "task_id": row["task_id"],
        "parent_note_id": row["parent_note_id"],
        "title": row["title"],
        "content": row["content"] or "",
        "category": row["category"] or "📝 Общие заметки",
        "tags": row["tags"] or "",
        "is_pinned": bool(row["is_pinned"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "task_name": row["task_name"],
    }


def get_today_stats(user_id):
    today = datetime.utcnow().date().isoformat()
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT total_focus_minutes, completed_cycles, pomodoro_sessions, short_breaks, long_breaks
            FROM focus_daily_stats WHERE user_id = ? AND date = ?
            """,
            (user_id, today),
        ).fetchone()
        if not row:
            return {
                "date": today,
                "total_focus_minutes": 0,
                "completed_cycles": 0,
                "pomodoro_sessions": 0,
                "short_breaks": 0,
                "long_breaks": 0,
            }
        return {
            "date": today,
            "total_focus_minutes": row["total_focus_minutes"],
            "completed_cycles": row["completed_cycles"],
            "pomodoro_sessions": row["pomodoro_sessions"],
            "short_breaks": row["short_breaks"],
            "long_breaks": row["long_breaks"],
        }


def update_today_stats(user_id, focus_minutes=0, completed_cycles=0, pomodoro_sessions=0, short_breaks=0, long_breaks=0):
    today = datetime.utcnow().date().isoformat()
    ts = now_iso()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM focus_daily_stats WHERE user_id = ? AND date = ?", (user_id, today)
        ).fetchone()
        if not row:
            conn.execute(
                """
                INSERT INTO focus_daily_stats
                (user_id, date, total_focus_minutes, completed_cycles, pomodoro_sessions, short_breaks, long_breaks, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    today,
                    max(0, int(focus_minutes)),
                    max(0, int(completed_cycles)),
                    max(0, int(pomodoro_sessions)),
                    max(0, int(short_breaks)),
                    max(0, int(long_breaks)),
                    ts,
                    ts,
                ),
            )
            return
        conn.execute(
            """
            UPDATE focus_daily_stats
            SET total_focus_minutes = total_focus_minutes + ?,
                completed_cycles = completed_cycles + ?,
                pomodoro_sessions = pomodoro_sessions + ?,
                short_breaks = short_breaks + ?,
                long_breaks = long_breaks + ?,
                updated_at = ?
            WHERE user_id = ? AND date = ?
            """,
            (
                max(0, int(focus_minutes)),
                max(0, int(completed_cycles)),
                max(0, int(pomodoro_sessions)),
                max(0, int(short_breaks)),
                max(0, int(long_breaks)),
                ts,
                user_id,
                today,
            ),
        )


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "TaskTideServer/3.0"

    def log_message(self, *_args):
        return

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _send_json(self, payload, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        if not raw:
            return {}
        return json.loads(raw)

    def _auth_user_id(self):
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth.split(" ", 1)[1].strip()
        return verify_access_token(token)

    def _require_auth(self):
        uid = self._auth_user_id()
        if not uid:
            self._send_json({"error": "Unauthorized"}, status=401)
            return None
        return uid

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/health":
            self._send_json({"ok": True, "server_time": now_iso()})
            return

        if path == "/auth/me":
            user_id = self._require_auth()
            if not user_id:
                return
            with get_conn() as conn:
                user = conn.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
            if not user:
                self._send_json({"error": "Unauthorized"}, status=401)
                return
            self._send_json({"user": dict(user)})
            return

        user_id = self._require_auth()
        if not user_id:
            return

        if path == "/api/tasks":
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC, id DESC", (user_id,)
                ).fetchall()
            self._send_json({"items": [task_row_to_json(r) for r in rows]})
            return

        if path == "/api/overview":
            with get_conn() as conn:
                stats = {
                    "total": conn.execute("SELECT COUNT(*) c FROM tasks WHERE user_id = ?", (user_id,)).fetchone()["c"],
                    "completed": conn.execute(
                        "SELECT COUNT(*) c FROM tasks WHERE user_id = ? AND status = 'выполнена'", (user_id,)
                    ).fetchone()["c"],
                    "in_progress": conn.execute(
                        "SELECT COUNT(*) c FROM tasks WHERE user_id = ? AND status = 'в процессе'", (user_id,)
                    ).fetchone()["c"],
                    "not_started": conn.execute(
                        "SELECT COUNT(*) c FROM tasks WHERE user_id = ? AND status = 'не начата'", (user_id,)
                    ).fetchone()["c"],
                }
                recent_rows = conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 6", (user_id,)
                ).fetchall()
            self._send_json(
                {
                    "stats": stats,
                    "focus": get_today_stats(user_id),
                    "recent_tasks": [task_row_to_json(r) for r in recent_rows],
                    "server_time": now_iso(),
                }
            )
            return

        if path == "/api/stats":
            with get_conn() as conn:
                payload = {
                    "total": conn.execute("SELECT COUNT(*) c FROM tasks WHERE user_id = ?", (user_id,)).fetchone()["c"],
                    "completed": conn.execute(
                        "SELECT COUNT(*) c FROM tasks WHERE user_id = ? AND status = 'выполнена'", (user_id,)
                    ).fetchone()["c"],
                    "in_progress": conn.execute(
                        "SELECT COUNT(*) c FROM tasks WHERE user_id = ? AND status = 'в процессе'", (user_id,)
                    ).fetchone()["c"],
                    "not_started": conn.execute(
                        "SELECT COUNT(*) c FROM tasks WHERE user_id = ? AND status = 'не начата'", (user_id,)
                    ).fetchone()["c"],
                }
            self._send_json(payload)
            return

        if path == "/api/deadlines/approaching":
            now_dt = datetime.now()
            tolerance = timedelta(minutes=1)
            intervals = [
                (timedelta(days=30), "месяц"),
                (timedelta(days=7), "неделя"),
                (timedelta(days=1), "день"),
                (timedelta(hours=6), "6 часов"),
                (timedelta(hours=1), "час"),
                (timedelta(minutes=30), "30 минут"),
                (timedelta(minutes=5), "5 минут"),
            ]
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? AND status != 'выполнена' ORDER BY deadline ASC", (user_id,)
                ).fetchall()
            result = []
            for row in rows:
                deadline = parse_iso(row["deadline"])
                if not deadline:
                    continue
                remaining = deadline - now_dt
                for delta, label in intervals:
                    if abs(remaining - delta) <= tolerance:
                        result.append({"task": task_row_to_json(row), "interval": label})
                        break
            self._send_json({"items": result})
            return

        if path == "/api/notes":
            task_id_values = query.get("task_id", [])
            with get_conn() as conn:
                if task_id_values:
                    try:
                        task_id = int(task_id_values[0])
                    except ValueError:
                        self._send_json({"error": "Invalid task_id"}, status=400)
                        return
                    rows = conn.execute(
                        """
                        SELECT n.*, t.name AS task_name
                        FROM notes n LEFT JOIN tasks t ON t.id = n.task_id
                        WHERE n.user_id = ? AND n.task_id = ?
                        ORDER BY n.is_pinned DESC, n.updated_at DESC
                        """,
                        (user_id, task_id),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT n.*, t.name AS task_name
                        FROM notes n LEFT JOIN tasks t ON t.id = n.task_id
                        WHERE n.user_id = ?
                        ORDER BY CASE WHEN n.parent_note_id IS NULL THEN 0 ELSE 1 END,
                                 n.parent_note_id ASC,
                                 n.is_pinned DESC,
                                 n.updated_at DESC
                        """,
                        (user_id,),
                    ).fetchall()
            self._send_json({"items": [note_row_to_json(r) for r in rows]})
            return

        if path == "/api/focus/stats":
            self._send_json(get_today_stats(user_id))
            return

        if path == "/api/focus/sessions":
            limit = 20
            if query.get("limit"):
                try:
                    limit = max(1, min(10000, int(query["limit"][0])))
                except ValueError:
                    pass
            with get_conn() as conn:
                rows = conn.execute(
                    """
                    SELECT fs.id, fs.task_id, fs.duration_minutes, fs.session_type, fs.created_at, t.name AS task_name
                    FROM focus_sessions fs
                    LEFT JOIN tasks t ON t.id = fs.task_id
                    WHERE fs.user_id = ?
                    ORDER BY fs.created_at DESC, fs.id DESC
                    LIMIT ?
                    """,
                    (user_id, limit),
                ).fetchall()
            self._send_json(
                {
                    "items": [
                        {
                            "id": row["id"],
                            "task_id": row["task_id"],
                            "duration_minutes": row["duration_minutes"],
                            "session_type": row["session_type"],
                            "created_at": row["created_at"],
                            "task_name": row["task_name"],
                        }
                        for row in rows
                    ]
                }
            )
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/auth/register":
            try:
                payload = self._read_json()
                username = str(payload.get("username", "")).strip()
                login = str(payload.get("login", payload.get("email", ""))).strip()
                password = str(payload.get("password", ""))
                if len(username) < 2:
                    self._send_json({"error": "Username must be at least 2 characters"}, status=400)
                    return
                if len(login) < 3:
                    self._send_json({"error": "Invalid login"}, status=400)
                    return
                if len(password) < 6:
                    self._send_json({"error": "Password must be at least 6 characters"}, status=400)
                    return

                salt, pwd_hash = hash_password(password)
                created_at = now_iso()
                with get_conn() as conn:
                    try:
                        cur = conn.execute(
                            "INSERT INTO users (username, email, password_hash, password_salt, created_at) VALUES (?, ?, ?, ?, ?)",
                            (username, login, pwd_hash, salt, created_at),
                        )
                    except sqlite3.IntegrityError:
                        self._send_json({"error": "Login already exists"}, status=409)
                        return
                    user_id = cur.lastrowid
                token = create_access_token(user_id)
                self._send_json(
                    {
                        "token": token,
                        "user": {"id": user_id, "username": username, "login": login, "email": login, "created_at": created_at},
                    },
                    status=201,
                )
                return
            except (json.JSONDecodeError, ValueError):
                self._send_json({"error": "Invalid request"}, status=400)
                return

        if path == "/auth/login":
            try:
                payload = self._read_json()
                login = str(payload.get("login", payload.get("email", ""))).strip()
                password = str(payload.get("password", ""))
                with get_conn() as conn:
                    user = conn.execute(
                        "SELECT id, username, email, password_hash, password_salt, created_at FROM users WHERE email = ?", (login,)
                    ).fetchone()
                if not user or not verify_password(password, user["password_salt"], user["password_hash"]):
                    self._send_json({"error": "Invalid login or password"}, status=401)
                    return
                token = create_access_token(user["id"])
                self._send_json(
                    {
                        "token": token,
                        "user": {
                            "id": user["id"],
                            "username": user["username"],
                            "login": user["email"],
                            "email": user["email"],
                            "created_at": user["created_at"],
                        },
                    }
                )
                return
            except (json.JSONDecodeError, ValueError):
                self._send_json({"error": "Invalid request"}, status=400)
                return

        user_id = self._require_auth()
        if not user_id:
            return

        if path == "/api/tasks":
            try:
                payload = self._read_json()
                name = str(payload.get("name", "")).strip()
                if not name:
                    self._send_json({"error": "Task name is required"}, status=400)
                    return

                priority = str(payload.get("priority", "Важно - Срочно")).strip() or "Важно - Срочно"
                category = str(payload.get("category", "Работа")).strip() or "Работа"
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
                        parts = str(duration_raw).strip().replace(" ", "").split(":")
                        if len(parts) != 3 or not (
                            len(parts[0]) == 3
                            and len(parts[1]) == 2
                            and len(parts[2]) == 2
                            and all(part.isdigit() for part in parts)
                        ):
                            self._send_json(
                                {"error": "Invalid duration format. Use 000:00:00 (days:hours:minutes)"}, status=400
                            )
                            return
                        days = int(parts[0])
                        hours = int(parts[1])
                        mins = int(parts[2])
                        total_minutes = mins + hours * 60 + days * 24 * 60
                        if total_minutes <= 0:
                            self._send_json({"error": "Duration must be greater than 0"}, status=400)
                            return
                    else:
                        total_minutes = max(1, int(payload.get("minutes", 60)))
                    deadline = datetime.now() + timedelta(minutes=total_minutes)
                ts = now_iso()
                with get_conn() as conn:
                    conn.execute(
                        """
                        INSERT INTO tasks (user_id, name, priority, category, deadline, status, description, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, 'не начата', ?, ?, ?)
                        """,
                        (user_id, name, priority, category, deadline.replace(microsecond=0).isoformat(), description, ts, ts),
                    )
                self._send_json({"ok": True}, status=201)
                return
            except (json.JSONDecodeError, ValueError):
                self._send_json({"error": "Invalid request"}, status=400)
                return

        if path == "/api/notes":
            try:
                payload = self._read_json()
                title = str(payload.get("title", "")).strip()
                if not title:
                    self._send_json({"error": "Note title is required"}, status=400)
                    return
                content = str(payload.get("content", "")).strip()
                category = str(payload.get("category", "📝 Общие заметки")).strip() or "📝 Общие заметки"
                tags = str(payload.get("tags", "")).strip()
                task_id = payload.get("task_id")
                parent_note_id = payload.get("parent_note_id")
                ts = now_iso()
                with get_conn() as conn:
                    conn.execute(
                        """
                        INSERT INTO notes
                        (user_id, task_id, parent_note_id, title, content, category, tags, is_pinned, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                        """,
                        (user_id, task_id, parent_note_id, title, content, category, tags, ts, ts),
                    )
                self._send_json({"ok": True}, status=201)
                return
            except (json.JSONDecodeError, ValueError):
                self._send_json({"error": "Invalid request"}, status=400)
                return

        if path == "/api/focus/session":
            try:
                payload = self._read_json()
                task_id = payload.get("task_id")
                session_type = str(payload.get("session_type", "pomodoro"))
                duration_minutes = max(1, int(payload.get("duration_minutes", 25)))
                notes = str(payload.get("notes", ""))
                ts = now_iso()

                with get_conn() as conn:
                    conn.execute(
                        """
                        INSERT INTO focus_sessions (user_id, task_id, duration_minutes, session_type, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, task_id, duration_minutes, session_type, notes, ts),
                    )

                if session_type == "pomodoro":
                    update_today_stats(user_id, focus_minutes=duration_minutes, completed_cycles=1, pomodoro_sessions=1)
                elif session_type == "short_break":
                    update_today_stats(user_id, short_breaks=1)
                elif session_type == "long_break":
                    update_today_stats(user_id, long_breaks=1)

                self._send_json({"ok": True}, status=201)
                return
            except (json.JSONDecodeError, ValueError):
                self._send_json({"error": "Invalid request"}, status=400)
                return

        self._send_json({"error": "Not found"}, status=404)

    def do_PATCH(self):
        path = urlparse(self.path).path
        user_id = self._require_auth()
        if not user_id:
            return

        try:
            payload = self._read_json()
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        if path.startswith("/api/tasks/") and path.endswith("/status"):
            raw = path[len("/api/tasks/") : -len("/status")]
            try:
                task_id = int(raw)
                status = str(payload.get("status", "")).strip()
                if status not in {"не начата", "в процессе", "выполнена"}:
                    self._send_json({"error": "Invalid status"}, status=400)
                    return
                with get_conn() as conn:
                    conn.execute(
                        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                        (status, now_iso(), task_id, user_id),
                    )
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid task id"}, status=400)
                return

        if path.startswith("/api/notes/") and path.endswith("/pin"):
            raw = path[len("/api/notes/") : -len("/pin")]
            try:
                note_id = int(raw)
                is_pinned = 1 if bool(payload.get("is_pinned", True)) else 0
                with get_conn() as conn:
                    conn.execute(
                        "UPDATE notes SET is_pinned = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                        (is_pinned, now_iso(), note_id, user_id),
                    )
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid note id"}, status=400)
                return

        if path.startswith("/api/notes/"):
            raw = path[len("/api/notes/") :]
            try:
                note_id = int(raw)
                title = str(payload.get("title", "")).strip()
                if not title:
                    self._send_json({"error": "Note title is required"}, status=400)
                    return
                content = str(payload.get("content", "")).strip()
                category = str(payload.get("category", "📝 Общие заметки")).strip() or "📝 Общие заметки"
                tags = str(payload.get("tags", "")).strip()
                with get_conn() as conn:
                    conn.execute(
                        """
                        UPDATE notes
                        SET title = ?, content = ?, category = ?, tags = ?, updated_at = ?
                        WHERE id = ? AND user_id = ?
                        """,
                        (title, content, category, tags, now_iso(), note_id, user_id),
                    )
                self._send_json({"ok": True})
                return
            except ValueError:
                self._send_json({"error": "Invalid note id"}, status=400)
                return

        self._send_json({"error": "Not found"}, status=404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        user_id = self._require_auth()
        if not user_id:
            return

        if path == "/api/focus/sessions":
            with get_conn() as conn:
                conn.execute("DELETE FROM focus_sessions WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM focus_daily_stats WHERE user_id = ?", (user_id,))
            self._send_json({"ok": True})
            return

        if path.startswith("/api/tasks/"):
            raw = path[len("/api/tasks/") :]
            try:
                task_id = int(raw)
            except ValueError:
                self._send_json({"error": "Invalid task id"}, status=400)
                return
            with get_conn() as conn:
                conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            self._send_json({"ok": True})
            return

        if path.startswith("/api/notes/"):
            raw = path[len("/api/notes/") :]
            try:
                note_id = int(raw)
            except ValueError:
                self._send_json({"error": "Invalid note id"}, status=400)
                return
            with get_conn() as conn:
                conn.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
            self._send_json({"ok": True})
            return

        self._send_json({"error": "Not found"}, status=404)


def run():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), ApiHandler)
    print(f"TaskTide server listening on http://{HOST}:{PORT}")
    print(f"Database path: {DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    run()
