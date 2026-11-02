"""Launch using an environment that already has requirements.txt installed."""

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--retrain", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    try:
        import streamlit  # noqa: F401
        from complaints.inference import load_bundle
        rebuild = args.retrain
        if not rebuild:
            try:
                load_bundle(ROOT)
            except (ValueError, OSError):
                rebuild = True
        if rebuild:
            subprocess.run([sys.executable, str(ROOT / "train.py")], cwd=ROOT, check=True)
        print(f"Dashboard: http://localhost:{args.port}  |  Press Ctrl+C to stop.", flush=True)
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
            "--server.address=127.0.0.1", f"--server.port={args.port}",
            f"--server.headless={'true' if args.no_browser else 'false'}",
        ], cwd=ROOT, check=True)
    except ImportError:
        parser.exit(2, "Packages are missing. Use python start.py for automatic setup.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
