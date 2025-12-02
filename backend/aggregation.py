"""
Data aggregation module for Swing County Calculator.

Aggregates precinct-level or raw election data to county-year level with
Democratic, Republican, and Other vote totals.
"""

import pandas as pd
from typing import Dict
from .config import COLUMN_NAMES, PARTY_LABELS


def aggregate_to_county_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate raw election data to county-year level.
    
    Groups data by [state_code, county_fips, county_name, year, party_simplified]
    and sums votes. Then pivots to create separate columns for dem_votes,
    rep_votes, other_votes, total_votes, margin, and margin_pct.
    
    Args:
        df: Raw election DataFrame with columns defined in config.COLUMN_NAMES
    
    Returns:
        DataFrame with one row per county-year containing:
            - state_code
            - county_fips
            - county_name
            - year
            - dem_votes (total Democratic votes)
            - rep_votes (total Republican votes)
            - other_votes (total Other party votes)
            - total_votes (sum of all votes)
            - margin (dem_votes - rep_votes)
            - margin_pct (margin / total_votes)
    
    Example:
        >>> raw_df = load_state_raw_data("AZ")
        >>> county_df = aggregate_to_county_year(raw_df)
        >>> county_df[['county_name', 'year', 'margin_pct']].head()
    """
    # Get column name mappings from config
    col_year = COLUMN_NAMES["year"]
    col_county_name = COLUMN_NAMES["county_name"]
    col_county_fips = COLUMN_NAMES["county_fips"]
    col_party = COLUMN_NAMES["party"]
    col_votes = COLUMN_NAMES["votes"]
    
    # Ensure state_code exists (should have been added in data_loading)
    if 'state_code' not in df.columns:
        raise ValueError("DataFrame must have 'state_code' column")
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Standardize party labels to DEM, REP, OTHER
    def standardize_party(party_value):
        if pd.isna(party_value):
            return "OTHER"
        party_str = str(party_value).upper()
        
        # Check against configured party labels
        if any(label.upper() in party_str or party_str in label.upper() 
               for label in PARTY_LABELS["dem"]):
            return "DEM"
        elif any(label.upper() in party_str or party_str in label.upper() 
                 for label in PARTY_LABELS["rep"]):
            return "REP"
        else:
            return "OTHER"
    
    df['party_std'] = df[col_party].apply(standardize_party)
    
    # Convert votes to numeric (handles strings, NaN, etc.)
    df[col_votes] = pd.to_numeric(df[col_votes], errors='coerce').fillna(0)
    
    # Group by county-year-party and sum votes
    grouped = df.groupby([
        'state_code',
        col_county_fips,
        col_county_name,
        col_year,
        'party_std'
    ], as_index=False)[col_votes].sum()
    
    # Pivot to get party columns
    pivoted = grouped.pivot_table(
        index=['state_code', col_county_fips, col_county_name, col_year],
        columns='party_std',
        values=col_votes,
        fill_value=0,
        aggfunc='sum'
    ).reset_index()
    
    # Rename columns to standard names
    pivoted.columns.name = None  # Remove 'party_std' label
    
    # Ensure all party columns exist (even if zero)
    for party in ['DEM', 'REP', 'OTHER']:
        if party not in pivoted.columns:
            pivoted[party] = 0
    
    # Rename to final column names
    result = pivoted.rename(columns={
        col_county_fips: 'county_fips',
        col_county_name: 'county_name',
        col_year: 'year',
        'DEM': 'dem_votes',
        'REP': 'rep_votes',
        'OTHER': 'other_votes'
    })
    
    # Calculate derived metrics
    result['total_votes'] = (
        result['dem_votes'] + 
        result['rep_votes'] + 
        result['other_votes']
    )
    
    # Margin = dem_votes - rep_votes (positive = Dem won, negative = Rep won)
    result['margin'] = result['dem_votes'] - result['rep_votes']
    
    # Margin percentage (avoid division by zero)
    result['margin_pct'] = result['margin'] / result['total_votes'].replace(0, 1)
    
    # Sort by state, county, year
    result = result.sort_values(['state_code', 'county_name', 'year'])
    
    print(f"✓ Aggregated to {len(result):,} county-year records")
    
    return result.reset_index(drop=True)
