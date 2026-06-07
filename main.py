import sys
import os
import subprocess
import signal
import time
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen
from src.tasktide.database import init_db

def start_notification_service():
    """Проверяет статус сервиса уведомлений (не запускает автоматически)"""
    try:
        # Проверяем статус сервиса, но не запускаем его автоматически
        result = subprocess.run([
            sys.executable, 
            "notification_service.py", 
            "status"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if "не запущен" in result.stdout:
            print("🔕 Фоновый сервис уведомлений отключен")
            print("💡 Уведомления будут работать только при открытом приложении")
        else:
            print("⚠️ Обнаружен запущенный фоновый сервис уведомлений")
            print("💡 Рекомендуется остановить его для работы только с открытым приложением")
            
    except Exception as e:
        print(f"⚠️ Ошибка проверки сервиса уведомлений: {e}")
        print("💡 Уведомления будут работать только при открытом приложении")


def run_electron_frontend():
    """Запускает Electron frontend. Возвращает True, если запуск завершился успешно."""
    project_dir = os.path.dirname(__file__)
    electron_dir = os.path.join(project_dir, "electron")

    if not os.path.isdir(electron_dir):
        print("⚠️ Папка electron не найдена, переключаемся на PyQt версию")
        return False

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    env = os.environ.copy()
    env.setdefault("PYTHON_BIN", sys.executable)
    api_process = None

    try:
        api_process = ensure_local_api_server(project_dir, env)
        result = subprocess.run([npm_cmd, "start"], cwd=electron_dir, env=env)
        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️ npm не найден. Установите Node.js и npm для Electron версии")
        return False
    except Exception as e:
        print(f"⚠️ Ошибка запуска Electron: {e}")
        return False
    finally:
        stop_local_api_server(api_process)


def _is_api_alive(api_base):
    health_url = f"{api_base.rstrip('/')}/health"
    try:
        with urlopen(health_url, timeout=0.8) as response:
            return 200 <= int(response.status) < 300
    except (URLError, OSError, TimeoutError, ValueError):
        return False


def _is_local_api(api_base):
    try:
        parsed = urlparse(api_base)
        return parsed.hostname in {"127.0.0.1", "localhost"}
    except ValueError:
        return False


def ensure_local_api_server(project_dir, env):
    api_base = env.get("TASKTIDE_API_BASE", "http://127.0.0.1:8765")
    if not _is_local_api(api_base):
        return None
    if _is_api_alive(api_base):
        return None

    api_script = os.path.join(project_dir, "server", "api_server.py")
    if not os.path.isfile(api_script):
        print(f"⚠️ Не найден API сервер: {api_script}")
        return None

    parsed = urlparse(api_base)
    api_env = env.copy()
    api_env.setdefault("TASKTIDE_HOST", "127.0.0.1")
    if parsed.port:
        api_env.setdefault("TASKTIDE_PORT", str(parsed.port))

    print(f"▶️ Запускаем локальный API сервер: {api_base}")
    process = subprocess.Popen([sys.executable, api_script], cwd=project_dir, env=api_env)

    for _ in range(25):
        if process.poll() is not None:
            print("⚠️ API сервер завершился сразу после запуска")
            return None
        if _is_api_alive(api_base):
            return process
        time.sleep(0.2)

    print(f"⚠️ API сервер не ответил по адресу {api_base}")
    stop_local_api_server(process)
    return None


def stop_local_api_server(process):
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()


def run_pyqt_fallback():
    """Запускает старую PyQt версию приложения."""
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    from src.tasktide.ui import MainWindow

    start_notification_service()

    app = QApplication(sys.argv)

    def _handle_sigint(signum, frame):
        app.quit()

    signal.signal(signal.SIGINT, _handle_sigint)

    sigint_timer = QTimer()
    sigint_timer.timeout.connect(lambda: None)
    sigint_timer.start(200)

    try:
        window = MainWindow()
        window.show()
        return app.exec_()
    except KeyboardInterrupt:
        return 0

if __name__ == "__main__":
    init_db()

    if "--pyqt" in sys.argv:
        sys.exit(run_pyqt_fallback())

    if run_electron_frontend():
        sys.exit(0)

    print("↩️ Electron не запустился, запускаем PyQt fallback...")
    sys.exit(run_pyqt_fallback())
