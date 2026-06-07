if __name__ == "__main__":
    import runpy
    runpy.run_module("src.tasktide.backend_api", run_name="__main__")
else:
    from src.tasktide.backend_api import *  # noqa: F401,F403
