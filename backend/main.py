"""CLI entrypoint for computing and inspecting county-level swing scores

This script uses the existing pipeline in `swing_score.py` to compute
county-level swing scores for a given state (or the default set). It
prints a ranked list and allows the user to inspect county details.
"""
import argparse
from typing import List

from .config import DEFAULT_STATES
from .swing_score import compute_state_swing_scores
from . import display
from .json_loader import load_state_from_json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute county-level swing scores for a state")
    p.add_argument("--state", "-s", help="Two-letter state code (e.g. PA)", required=False)
    p.add_argument("--top", "-t", type=int, default=20, help="How many top counties to show")
    return p.parse_args()


def run_for_state(state: str, top: int = 20) -> None:
    try:
        swing_df = compute_state_swing_scores(state)
    except Exception as e:
        print(f"Error computing swing scores for {state}: {e}")
        return

    # Display summary and top counties
    display.show_state_summary(swing_df)
    display.show_ranked_counties(swing_df, top=top)
    display.prompt_for_county_selection(swing_df)


def main():
    args = parse_args()

    if args.state:
        states: List[str] = [args.state.upper()]
    else:
        states = DEFAULT_STATES

    # If the precomputed JSON exists, prefer it (simpler for exploration).
    json_path = Path(__file__).parent.parent / "swingscorejsons" / "swing_scores_all_states.json"

    for st in states:
        print(f"\n== {st} ==")
        if json_path.exists():
            try:
                df = load_state_from_json(st, path=str(json_path))
                if df.empty:
                    print(f"No precomputed data for {st} in {json_path}. Falling back to pipeline.")
                    run_for_state(st, top=args.top)
                else:
                    display.show_state_summary(df)
                    display.show_ranked_counties(df, top=args.top)
                    display.prompt_for_county_selection(df)
            except Exception as e:
                print(f"Error loading JSON for {st}: {e}. Falling back to pipeline.")
                run_for_state(st, top=args.top)
        else:
            run_for_state(st, top=args.top)


if __name__ == "__main__":
    main()
