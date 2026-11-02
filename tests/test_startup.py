"""Exercise interrupted-setup recovery without downloading anything in unit tests."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import start


def test_partial_environment_repairs_missing_pip_before_install(tmp_path):
    environment = tmp_path / ".venv"
    executable = environment / ("Scripts/python.exe" if start.os.name == "nt" else "bin/python")
    executable.parent.mkdir(parents=True)
    executable.touch()
    (tmp_path / "requirements.txt").write_text("pandas==2.3.3\n")
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=1 if command[1:] == ["-m", "pip", "--version"] else 0)

    with patch.object(start, "ROOT", tmp_path), patch.object(start, "installed_requirements", return_value=False), patch.object(start.sys, "argv", ["start.py", "--setup-only"]), patch.object(start.subprocess, "run", side_effect=fake_run):
        start.main()
    assert any(command[1:4] == ["-m", "ensurepip", "--upgrade"] for command in calls)
    assert any(command[1:4] == ["-m", "pip", "install"] for command in calls)
    assert (environment / "requirements.sha256").exists()


def test_installed_environment_does_not_require_pip_or_internet(tmp_path):
    environment = tmp_path / ".venv"
    executable = environment / ("Scripts/python.exe" if start.os.name == "nt" else "bin/python")
    executable.parent.mkdir(parents=True)
    executable.touch()
    (tmp_path / "requirements.txt").write_text("pandas==2.3.3\n")
    with patch.object(start, "ROOT", tmp_path), patch.object(start, "installed_requirements", return_value=True), patch.object(start.sys, "argv", ["start.py", "--setup-only"]), patch.object(start.subprocess, "run") as run:
        start.main()
    run.assert_not_called()
