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
from pathlib import Path as _Path


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

    # If county_fips are missing or empty in this dataset, attempt to
    # infer them from a local county GeoJSON (if available). This helps
    # the map rendering code which expects 5-digit FIPS strings.
    if df['county_fips'].isna().all() or df['county_fips'].astype(str).str.strip().eq('').all():
        try:
            _try_add_fips_from_geojson(df, state_code)
        except Exception:
            # best-effort only; if mapping fails, leave county_fips as-is
            pass

    # Normalize county_fips to zero-padded 5-digit strings when present
    if 'county_fips' in df.columns:
        df['county_fips'] = df['county_fips'].apply(format_fips)

    # Sort by swing_score descending if available
    if 'swing_score' in df.columns:
        df = df.sort_values('swing_score', ascending=False).reset_index(drop=True)

    return df


def _try_add_fips_from_geojson(df: pd.DataFrame, state_code: str) -> None:
    """
    Mutates the provided DataFrame to add a `county_fips` column by matching
    county names to a local county GeoJSON (if present).

    Matching is fuzzy but prefers exact-case-insensitive matches after
    stripping common suffixes like ' COUNTY'. If a match is found the
    feature's `id` (expected to be the 5-digit FIPS) is used.

    This function is best-effort and will not raise on failures.
    """
    geojson_path = _Path(__file__).parent.parent / 'swingscorejsons' / 'counties.geojson'
    if not geojson_path.exists():
        return

    # Load the geojson features
    try:
        with open(geojson_path, 'r', encoding='utf-8') as fh:
            gj = json.load(fh)
    except Exception:
        return

    features = gj.get('features') or []
    # Build a mapping from normalized county name -> fips
    name_to_fips = {}
    for feat in features:
        props = feat.get('properties', {})
        # Common property names for county name vary; try several
        name = props.get('NAME') or props.get('name') or props.get('county') or props.get('COUNTY')
        fip = feat.get('id') or props.get('GEOID') or props.get('FIPS') or props.get('fips')
        if not name or not fip:
            continue
        # normalize
        key = _normalize_county_name(str(name))
        name_to_fips[key] = str(fip).zfill(5)

    # For each row try to fill county_fips
    def _map_row(row):
        if pd.notna(row.get('county_fips')) and str(row.get('county_fips')).strip() != '':
            return row.get('county_fips')
        cname = row.get('county_name')
        if not cname:
            return pd.NA
        key = _normalize_county_name(str(cname))
        return name_to_fips.get(key, pd.NA)

    df['county_fips'] = df.apply(_map_row, axis=1)
    # Ensure formatting
    df['county_fips'] = df['county_fips'].apply(lambda v: format_fips(v) if pd.notna(v) else v)


def _normalize_county_name(name: str) -> str:
    """Normalize county names for matching: uppercase, strip ' COUNTY', trim whitespace."""
    s = name.strip().upper()
    if s.endswith(' COUNTY'):
        s = s[:-7].strip()
    if s.endswith(' PARISH'):
        s = s[:-6].strip()
    # Remove common punctuation
    for ch in ["'", '"', '.', ',']:
        s = s.replace(ch, '')
    return s
