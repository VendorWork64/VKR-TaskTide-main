#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    electron_dir = project_root / "electron"
    server_script = project_root / "server" / "api_server.py"
    out_dir = electron_dir / "server-bin"

    if not server_script.exists():
        print(f"Server script not found: {server_script}", file=sys.stderr)
        return 1

    try:
        import PyInstaller  # noqa: F401
    except Exception:
        print("PyInstaller is not installed in this Python environment.", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    for item in out_dir.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    build_dir = project_root / ".build" / "pyinstaller"
    spec_dir = project_root / ".build" / "spec"
    build_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--name",
            "tasktide-api-server",
            str(server_script),
            "--distpath",
            str(out_dir),
            "--workpath",
            str(build_dir),
            "--specpath",
            str(spec_dir),
        ],
        cwd=project_root,
    )

    built_files = sorted(p.name for p in out_dir.iterdir())
    print("Built:", ", ".join(built_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
