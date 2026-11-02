"""Beginner entry point: python start.py (first run needs internet for packages)."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def installed_requirements(executable: Path, requirements: Path) -> bool:
    """Check versions even when an earlier installation left a stale marker."""
    script = "import importlib.metadata as m; import sys; "
    script += "items=[line.strip().split('==') for line in open(sys.argv[1]) if line.strip() and not line.startswith('#')]; "
    script += "assert all(m.version(name)==version for name,version in items)"
    return subprocess.run([str(executable), "-c", script, str(requirements)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def main():
    if not (3, 10) <= sys.version_info[:2] <= (3, 13):
        raise SystemExit("Use Python 3.10-3.13. Python 3.12 is the tested version.")
    environment = ROOT / ".venv"
    executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    requirements = ROOT / "requirements.txt"
    marker = environment / "requirements.sha256"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    if not executable.exists():
        print("Creating the project's Python environment ...", flush=True)
        venv.EnvBuilder(with_pip=False).create(environment)
    if not installed_requirements(executable, requirements):
        # An interrupted first setup can leave Python present but pip missing.
        pip_ready = subprocess.run([str(executable), "-m", "pip", "--version"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not pip_ready:
            print("Preparing the package installer ...", flush=True)
            subprocess.run([str(executable), "-m", "ensurepip", "--upgrade"], check=True, cwd=ROOT)
        print("Installing project packages. This first step needs internet ...", flush=True)
        subprocess.run([str(executable), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(requirements)], check=True, cwd=ROOT)
    marker.write_text(digest, encoding="utf-8")
    if "--setup-only" in sys.argv:
        print("Setup complete. Launch with: python start.py")
        return
    subprocess.run([str(executable), str(ROOT / "run.py"), *sys.argv[1:]], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Setup or launch failed: {error}\nUse Python 3.12 and retry python start.py. If package downloads failed, check your internet connection. An interrupted setup will be repaired on retry.")
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
