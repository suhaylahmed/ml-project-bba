"""Regenerate the fictional training data and batch examples."""

import argparse
from pathlib import Path

from complaints.data import write_sample_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        print(write_sample_data(Path(__file__).resolve().parent, args.rows, args.seed))
    except ValueError as error:
        parser.exit(2, f"Data generation failed: {error}\n")
