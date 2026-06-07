import sys
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from src.tasktide.database import (
    add_task,
    delete_task,
    get_all_tasks,
    get_tasks_statistics,
    init_db,
    update_task_status,
)


class AppBridge(QObject):
    tasksChanged = Signal()
    statsChanged = Signal()

    def __init__(self):
        super().__init__()
        self._tasks = []
        self._stats = {}
        self.refresh_data()

    @Property("QVariantList", notify=tasksChanged)
    def tasks(self):
        return self._tasks

    @Property("QVariantMap", notify=statsChanged)
    def stats(self):
        return self._stats

    @Slot()
    def refresh(self):
        self.refresh_data()

    @Slot(str, str, str, int, str)
    def addTask(self, name, category1, category2, minutes_from_now, description):
        task_name = name.strip()
        if not task_name:
            return

        deadline = datetime.now() + timedelta(minutes=max(minutes_from_now, 1))
        add_task(
            task_name,
            category1,
            category2,
            deadline.isoformat(timespec="seconds"),
            description.strip(),
        )
        self.refresh_data()

    @Slot(int, str)
    def setTaskStatus(self, task_id, status):
        update_task_status(task_id, status)
        self.refresh_data()

    @Slot(int)
    def removeTask(self, task_id):
        delete_task(task_id)
        self.refresh_data()

    def refresh_data(self):
        mapped_tasks = []
        for row in get_all_tasks():
            deadline_raw = row[4] or ""
            try:
                deadline_dt = datetime.fromisoformat(deadline_raw)
                deadline_label = deadline_dt.strftime("%d.%m.%Y %H:%M")
            except ValueError:
                deadline_label = deadline_raw

            mapped_tasks.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "priority": row[2],
                    "category": row[3],
                    "deadline": deadline_label,
                    "status": row[5],
                    "description": row[6] or "",
                }
            )

        self._tasks = mapped_tasks
        self.tasksChanged.emit()

        stats = get_tasks_statistics()
        self._stats = {
            "total": stats.get("total", 0),
            "completed": stats.get("completed", 0),
            "in_progress": stats.get("in_progress", 0),
            "not_started": stats.get("not_started", 0),
        }
        self.statsChanged.emit()


def main():
    init_db()
    app = QGuiApplication(sys.argv)
    app.setApplicationName("TaskTide Next")

    engine = QQmlApplicationEngine()
    bridge = AppBridge()
    engine.rootContext().setContextProperty("bridge", bridge)

    qml_path = Path(__file__).parent / "qml" / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
