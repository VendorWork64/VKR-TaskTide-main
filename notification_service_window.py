if __name__ == "__main__":
    import runpy
    runpy.run_module("src.tasktide.notification_service_window", run_name="__main__")
else:
    from src.tasktide.notification_service_window import *  # noqa: F401,F403
