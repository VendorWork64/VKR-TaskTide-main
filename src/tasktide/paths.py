from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
LOCAL_DATA_DIR = DATA_DIR / "local"
RUNTIME_DIR = DATA_DIR / "runtime"
ASSETS_DIR = PROJECT_ROOT / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"

LEGACY_DB_PATH = PROJECT_ROOT / "tasks.db"
DB_PATH = LOCAL_DATA_DIR / "tasks.db"


def ensure_project_dirs() -> None:
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)


def _migrate_legacy_db_if_needed() -> None:
    if DB_PATH.exists() or not LEGACY_DB_PATH.exists():
        return
    ensure_project_dirs()
    shutil.copy2(LEGACY_DB_PATH, DB_PATH)


def get_db_path() -> Path:
    ensure_project_dirs()
    _migrate_legacy_db_if_needed()
    return DB_PATH if DB_PATH.exists() else LEGACY_DB_PATH


def get_runtime_file(filename: str) -> Path:
    ensure_project_dirs()
    return RUNTIME_DIR / filename


def get_sound_path(filename: str) -> Path:
    ensure_project_dirs()
    new_path = SOUNDS_DIR / filename
    if new_path.exists():
        return new_path
    legacy_path = PROJECT_ROOT / filename
    return legacy_path
