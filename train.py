"""Train, compare, evaluate, and save the project in one command."""

import argparse
from pathlib import Path

from complaints.data import write_sample_data
from complaints.training import train_project

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, help="Labelled CSV; default: data/complaints.csv")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-recall", type=float, default=0.85, help="Desired validation recall")
    args = parser.parse_args()
    path = args.data.resolve() if args.data else ROOT / "data" / "complaints.csv"
    if not path.exists() and args.data is None:
        write_sample_data(ROOT, seed=args.seed)
    try:
        train_project(ROOT, path, args.seed, args.min_recall)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Training failed: {error}\n")
