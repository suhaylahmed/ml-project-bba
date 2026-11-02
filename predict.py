"""Score a CSV without opening the dashboard."""

import argparse
from pathlib import Path

import pandas as pd

from complaints.inference import load_bundle, safe_csv, score_tickets

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float)
    args = parser.parse_args()
    try:
        root = Path(__file__).resolve().parent
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Choose a different output path so the input file is preserved.")
        results = score_tickets(pd.read_csv(args.input), load_bundle(root), args.threshold)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(safe_csv(results), encoding="utf-8")
        print(f"Scored {len(results)} tickets -> {args.output}")
    except (ValueError, OSError, pd.errors.ParserError) as error:
        parser.exit(2, f"Prediction failed: {error}\n")
