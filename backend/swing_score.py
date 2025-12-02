"""
Swing score calculation module for Swing County Calculator.

Computes county-level swing scores based on four components:
1. Margin change (how much the margin shifted between elections)
2. Closeness (how close the latest election was)
3. Turnout (voter participation, using total votes as proxy)
4. Votes (county population/size weight)
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from .config import (
    SWING_WEIGHTS, 
    PROCESSED_DATA_DIR,
    DEFAULT_YEAR_PREV,
    DEFAULT_YEAR_LATEST
)
from .data_loading import load_state_raw_data
from .aggregation import aggregate_to_county_year


def normalize_series(s: pd.Series) -> pd.Series:
    """
    Normalize a numeric Series to 0-1 range using min-max normalization.
    
    Args:
        s: Numeric pandas Series
    
    Returns:
        Normalized Series with values in [0, 1] range
        If all values are equal, returns 0.5 for all values
    
    Example:
        >>> s = pd.Series([10, 20, 30, 40, 50])
        >>> normalize_series(s)
        0    0.00
        1    0.25
        2    0.50
        3    0.75
        4    1.00
        dtype: float64
    """
    s_min = s.min()
    s_max = s.max()
    
    # Handle case where all values are the same
    if s_max == s_min:
        return pd.Series([0.5] * len(s), index=s.index)
    
    # Min-max normalization: (x - min) / (max - min)
    return (s - s_min) / (s_max - s_min)


def compute_swing_components(
    county_year_df: pd.DataFrame,
    year_prev: int,
    year_latest: int
) -> pd.DataFrame:
    """
    Compute swing score components for each county.
    
    Links two election years for each county and calculates:
    1. margin_change_abs: Absolute change in margin percentage
    2. closeness_latest: How close the latest election was (1 - abs(margin))
    3. turnout_latest: Total votes in latest election (turnout proxy)
    4. votes_latest: Total votes (population weight)
    
    Then normalizes each to 0-1 and combines into final swing_score.
    
    Args:
        county_year_df: Aggregated county-year DataFrame from aggregate_to_county_year()
        year_prev: Earlier election year (e.g., 2016)
        year_latest: Most recent election year (e.g., 2020)
    
    Returns:
        DataFrame with one row per county containing:
            - state_code, county_fips, county_name
            - year_prev, year_latest
            - Raw components: margin_change_abs, closeness_latest, 
              turnout_latest, votes_latest
            - Normalized scores: margin_change_score, closeness_score,
              turnout_score, votes_score
            - swing_score: Weighted combination of normalized scores
    
    Example:
        >>> county_df = aggregate_to_county_year(raw_df)
        >>> swing_df = compute_swing_components(county_df, 2016, 2020)
        >>> swing_df[['county_name', 'swing_score']].head()
    """
    # Filter to only the two years we care about
    df_years = county_year_df[
        county_year_df['year'].isin([year_prev, year_latest])
    ].copy()
    
    # Pivot to get prev and latest in separate columns
    df_prev = df_years[df_years['year'] == year_prev].copy()
    df_latest = df_years[df_years['year'] == year_latest].copy()
    
    # Rename columns for clarity
    df_prev = df_prev.rename(columns={
        'margin_pct': 'margin_pct_prev',
        'total_votes': 'total_votes_prev'
    })
    
    df_latest = df_latest.rename(columns={
        'margin_pct': 'margin_pct_latest',
        'total_votes': 'total_votes_latest'
    })
    
    # Merge on county identifiers
    df_merged = df_prev[[
        'state_code', 'county_fips', 'county_name', 
        'margin_pct_prev', 'total_votes_prev'
    ]].merge(
        df_latest[[
            'state_code', 'county_fips', 'county_name',
            'margin_pct_latest', 'total_votes_latest'
        ]],
        on=['state_code', 'county_fips', 'county_name'],
        how='inner'  # Only counties with data in both years
    )
    
    # =========================================================================
    # COMPUTE RAW COMPONENTS
    # =========================================================================
    
    # 1. Margin change (absolute value - bigger swing = higher score)
    df_merged['margin_change_abs'] = abs(
        df_merged['margin_pct_latest'] - df_merged['margin_pct_prev']
    )
    
    # 2. Closeness (how competitive the latest election was)
    #    1 - abs(margin_pct) means closer to 0.5 = more competitive
    df_merged['closeness_latest'] = 1 - abs(df_merged['margin_pct_latest'])
    
    # 3. Turnout (using total votes as proxy for turnout)
    #    Higher turnout = more engaged electorate
    df_merged['turnout_latest'] = df_merged['total_votes_latest']
    
    # 4. Votes/Population weight (larger counties get more weight)
    df_merged['votes_latest'] = df_merged['total_votes_latest']
    
    # =========================================================================
    # NORMALIZE COMPONENTS TO 0-1 SCALE
    # =========================================================================
    
    df_merged['margin_change_score'] = normalize_series(df_merged['margin_change_abs'])
    df_merged['closeness_score'] = normalize_series(df_merged['closeness_latest'])
    df_merged['turnout_score'] = normalize_series(df_merged['turnout_latest'])
    df_merged['votes_score'] = normalize_series(df_merged['votes_latest'])
    
    # =========================================================================
    # COMPUTE FINAL SWING SCORE (weighted average)
    # =========================================================================
    
    df_merged['swing_score'] = (
        SWING_WEIGHTS['margin_change'] * df_merged['margin_change_score'] +
        SWING_WEIGHTS['closeness'] * df_merged['closeness_score'] +
        SWING_WEIGHTS['turnout'] * df_merged['turnout_score'] +
        SWING_WEIGHTS['votes'] * df_merged['votes_score']
    )
    
    # Add year columns for reference
    df_merged['year_prev'] = year_prev
    df_merged['year_latest'] = year_latest
    
    # Select final columns
    result = df_merged[[
        'state_code',
        'county_fips',
        'county_name',
        'year_prev',
        'year_latest',
        'margin_change_abs',
        'closeness_latest',
        'turnout_latest',
        'votes_latest',
        'margin_change_score',
        'closeness_score',
        'turnout_score',
        'votes_score',
        'swing_score'
    ]].copy()
    
    # Sort by swing_score descending (highest = most persuadable)
    result = result.sort_values('swing_score', ascending=False)
    
    print(f"✓ Computed swing scores for {len(result):,} counties")
    print(f"  Score range: {result['swing_score'].min():.3f} - {result['swing_score'].max():.3f}")
    print(f"  Mean score: {result['swing_score'].mean():.3f}")
    
    return result.reset_index(drop=True)


def compute_state_swing_scores(
    state_code: str,
    year_prev: Optional[int] = None,
    year_latest: Optional[int] = None
) -> pd.DataFrame:
    """
    High-level function to compute swing scores for a state.
    
    Orchestrates the full pipeline:
    1. Load raw state data
    2. Aggregate to county-year level
    3. Compute swing components and final score
    
    Args:
        state_code: Two-letter state code (e.g., "AZ", "GA")
        year_prev: Earlier election year (defaults to config.DEFAULT_YEAR_PREV)
        year_latest: Recent election year (defaults to config.DEFAULT_YEAR_LATEST)
    
    Returns:
        DataFrame with swing scores for all counties in the state
    
    Example:
        >>> swing_scores = compute_state_swing_scores("PA", 2016, 2020)
        >>> swing_scores.head()
    """
    year_prev = year_prev or DEFAULT_YEAR_PREV
    year_latest = year_latest or DEFAULT_YEAR_LATEST
    
    print(f"\n{'='*60}")
    print(f"Computing swing scores for {state_code}")
    print(f"Comparing {year_prev} → {year_latest}")
    print(f"{'='*60}\n")
    
    # Step 1: Load raw data
    raw_df = load_state_raw_data(state_code)
    
    # Step 2: Aggregate to county-year
    county_year_df = aggregate_to_county_year(raw_df)
    
    # Step 3: Compute swing scores
    swing_df = compute_swing_components(county_year_df, year_prev, year_latest)
    
    return swing_df


def save_state_swing_scores_to_csv(
    state_code: str,
    year_prev: Optional[int] = None,
    year_latest: Optional[int] = None,
    path: Optional[str] = None
) -> str:
    """
    Compute swing scores for a state and save to CSV.
    
    Args:
        state_code: Two-letter state code (e.g., "AZ")
        year_prev: Earlier election year (optional, uses default from config)
        year_latest: Recent election year (optional, uses default from config)
        path: Custom output path (optional, defaults to data/processed/{state}_swing_scores.csv)
    
    Returns:
        Path to the saved CSV file
    
    Example:
        >>> filepath = save_state_swing_scores_to_csv("AZ", 2016, 2020)
        >>> print(f"Saved to {filepath}")
    """
    year_prev = year_prev or DEFAULT_YEAR_PREV
    year_latest = year_latest or DEFAULT_YEAR_LATEST
    
    # Compute swing scores
    swing_df = compute_state_swing_scores(state_code, year_prev, year_latest)
    
    # Determine output path
    if path is None:
        Path(PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
        path = f"{PROCESSED_DATA_DIR}/{state_code.lower()}_swing_scores.csv"
    
    # Save to CSV
    swing_df.to_csv(path, index=False)
    
    print(f"\n✅ Saved swing scores to: {path}")
    print(f"   {len(swing_df)} counties ranked by swing score")
    
    return path
