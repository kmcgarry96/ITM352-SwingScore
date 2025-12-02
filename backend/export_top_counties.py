"""Export top-N counties per default swing state from precomputed JSON.

Creates CSV files in the repository `outputs/` directory named
`outputs/{STATE}_top{N}.csv` and prints a short top-5 summary for each.
"""
from pathlib import Path
from typing import List
import argparse
import os

import pandas as pd

from .config import DEFAULT_STATES
from .json_loader import load_state_from_json
from .fips import format_fips


def export_top_for_states(states: List[str], top: int = 20, out_dir: str = "outputs", weights: List[float] | None = None) -> List[Path]:
    out_paths = []
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    for st in states:
        df = load_state_from_json(st)
        if df.empty:
            print(f"No data for {st}, skipping.")
            continue

        # Compute user-friendly columns
        df = df.copy()
        # Recompute swing score from normalized component columns if weights provided
        # Expected normalized component columns in JSON: margin_change_score, closeness_score, turnout_score, votes_score
        if weights:
            # Interpret weights: if two values provided -> [w_closeness, w_shift]
            # if four values provided -> [w_margin_change, w_closeness, w_turnout, w_votes]
            w = list(weights)
            if len(w) == 2:
                w_closeness, w_shift = w
                # map to available normalized columns
                df['swing_score_custom'] = (
                    (w_shift * df.get('margin_change_score', 0).astype(float)) +
                    (w_closeness * df.get('closeness_score', 0).astype(float))
                )
            elif len(w) == 4:
                w_margin, w_closeness, w_turnout, w_votes = w
                df['swing_score_custom'] = (
                    (w_margin * df.get('margin_change_score', 0).astype(float)) +
                    (w_closeness * df.get('closeness_score', 0).astype(float)) +
                    (w_turnout * df.get('turnout_score', 0).astype(float)) +
                    (w_votes * df.get('votes_score', 0).astype(float))
                )
            else:
                raise ValueError("--weights must have 2 (closeness,shift) or 4 (margin,closeness,turnout,votes) values")

            # Normalize weights to sum to 1 if they don't
            s = sum(w)
            if s != 0:
                df['swing_score_custom'] = df['swing_score_custom'] / s
            else:
                # fallback: use existing swing_score
                df['swing_score_custom'] = df['swing_score'].astype(float)

            df['swing_score'] = df['swing_score_custom']

        df['swing_score_100'] = df['swing_score'].astype(float) * 100
        df['margin_change_pct'] = df['margin_change_abs'].astype(float) * 100
        df['latest_abs_margin_pct'] = (1.0 - df['closeness_latest'].astype(float)) * 100

        # Select columns for export and sorting
        cols = [
            'county_name', 'county_fips', 'swing_score_100',
            'margin_change_pct', 'latest_abs_margin_pct', 'turnout_latest'
        ]

        # Ensure columns exist and tidy formats
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA

        # Zero-pad county_fips to 5-digit strings where possible
        df['county_fips'] = df['county_fips'].apply(format_fips)

        df_sorted = df.sort_values('swing_score_100', ascending=False).reset_index(drop=True)
        top_df = df_sorted.head(top)

        # Add an optional impact score (swing * turnout) to help prioritize
        try:
            df['impact_score'] = df['swing_score_100'].astype(float) * df['turnout_latest'].astype(float)
        except Exception:
            df['impact_score'] = pd.NA

        out_path = out_dir_path / f"{st}_top{top}.csv"
        top_df.to_csv(out_path, index=False, columns=cols)
        out_paths.append(out_path)

        # Print short top-5 summary
        print(f"\n{st} — top {min(5, len(top_df))} counties:")
        for i, row in top_df.head(5).iterrows():
            print(f" {i+1}. {row['county_name'][:30]:30}  score={row['swing_score_100']:.2f}  Δmargin%={row['margin_change_pct']:.2f}")

    print(f"\nExported {len(out_paths)} files to {out_dir_path.resolve()}")
    return out_paths


def parse_args():
    p = argparse.ArgumentParser(description="Export top-N swing counties per state")
    p.add_argument("--top", "-t", type=int, default=20, help="How many top counties to export per state")
    p.add_argument("--out", "-o", default="outputs", help="Output directory")
    p.add_argument("--states", "-s", nargs='*', default=None, help="State codes to export (default=DEFAULT_STATES)")
    p.add_argument("--weights", "-w", default=None,
                   help=("Comma-separated weights. Two values => 'closeness,shift'. "
                         "Four values => 'margin,closeness,turnout,votes'. "
                         "Example: --weights 0.5,0.5 or --weights 0.25,0.25,0.25,0.25"))
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    states = [s.upper() for s in args.states] if args.states else DEFAULT_STATES
    weights = None
    if args.weights:
        parts = [p.strip() for p in args.weights.replace(' ', ',').split(',') if p.strip()]
        try:
            weights = [float(x) for x in parts]
        except ValueError:
            raise SystemExit("Invalid --weights values; must be numbers separated by commas")

    export_top_for_states(states, top=args.top, out_dir=args.out, weights=weights)
