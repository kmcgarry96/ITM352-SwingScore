"""
Load precomputed swing scores stored as JSON in `swingscorejsons/`.

The expected JSON layout (as present in the repo) is a mapping from
state code to a list of county records, where each record contains the
fields produced by the pipeline (e.g., 'county_name', 'county_fips',
'swing_score', 'margin_change_abs', 'closeness_latest', 'turnout_latest').
"""
from pathlib import Path
import json
from typing import Optional
import pandas as pd
from .fips import format_fips


def load_state_from_json(state_code: str, path: Optional[str] = None) -> pd.DataFrame:
    """Load a state's county swing scores from a precomputed JSON file.

    Args:
        state_code: Two-letter state code (e.g., 'PA')
        path: Optional path to the JSON file. Defaults to swingscorejsons/swing_scores_all_states.json

    Returns:
        DataFrame of county records for the state, or an empty DataFrame if not found.
    """
    base = Path(path) if path else Path(__file__).parent.parent / "swingscorejsons" / "swing_scores_all_states.json"

    if not base.exists():
        raise FileNotFoundError(f"JSON file not found: {base}")

    with open(base, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    state_code = state_code.upper()
    entries = data.get(state_code)
    if not entries:
        # return empty dataframe with no rows
        return pd.DataFrame()

    df = pd.json_normalize(entries)

    # Ensure expected columns exist and provide convenient names
    # Keep original swing_score (0..1) but add a 0..100 formatted column later in display
    expected_cols = [
        'county_name', 'county_fips', 'swing_score',
        'margin_change_abs', 'closeness_latest', 'turnout_latest', 'votes_latest'
    ]

    # Add missing expected cols with NaN so downstream code can reference them
    for c in expected_cols:
        if c not in df.columns:
            df[c] = pd.NA

    # Normalize county_fips to zero-padded 5-digit strings when present
    if 'county_fips' in df.columns:
        df['county_fips'] = df['county_fips'].apply(format_fips)

    # Sort by swing_score descending if available
    if 'swing_score' in df.columns:
        df = df.sort_values('swing_score', ascending=False).reset_index(drop=True)

    return df
