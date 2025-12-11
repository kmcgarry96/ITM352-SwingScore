"""
Tier classification system for swing score counties.

Categorizes counties into tiers (S, A, B, C, D) based on their swing scores
to help prioritize campaign resources and identify high-value targets.
"""

import pandas as pd
from typing import Dict, List, Tuple


# Tier definitions based on swing_score (0-1 scale)
TIER_THRESHOLDS = {
    'S': (0.70, 1.00),   # Elite: 70-100% - Unicorn counties, extremely rare
    'A': (0.55, 0.70),   # Excellent: 55-70% - Top priority targets
    'B': (0.40, 0.55),   # Good: 40-55% - Strong swing potential
    'C': (0.25, 0.40),   # Moderate: 25-40% - Secondary targets
    'D': (0.00, 0.25),   # Low: 0-25% - Lower priority
}

# Tier descriptions for display/reporting
TIER_DESCRIPTIONS = {
    'S': 'Elite - Unicorn counties with exceptional scores across all metrics',
    'A': 'Excellent - Top priority targets with strong swing potential',
    'B': 'Good - Solid swing counties worth significant investment',
    'C': 'Moderate - Secondary targets for remaining resources',
    'D': 'Low Priority - Limited swing potential or low competitiveness'
}

# Emoji indicators for visual display
TIER_EMOJIS = {
    'S': '🏆',
    'A': '⭐',
    'B': '✅',
    'C': '📊',
    'D': '📉'
}


def assign_tier(swing_score: float) -> str:
    """
    Assign a tier (S, A, B, C, D) to a county based on its swing score.
    
    Args:
        swing_score: Normalized swing score (0-1 scale)
    
    Returns:
        Single letter tier classification
    
    Example:
        >>> assign_tier(0.76)
        'S'
        >>> assign_tier(0.45)
        'B'
    """
    for tier, (min_score, max_score) in TIER_THRESHOLDS.items():
        if min_score <= swing_score < max_score:
            return tier
    
    # Edge case: score of exactly 1.0
    if swing_score >= 1.0:
        return 'S'
    
    # Should not happen but default to lowest tier
    return 'D'


def add_tier_column(df: pd.DataFrame, score_col: str = 'swing_score') -> pd.DataFrame:
    """
    Add a 'tier' column to a DataFrame containing swing scores.
    
    Args:
        df: DataFrame with swing score column
        score_col: Name of the column containing swing scores (0-1 scale)
    
    Returns:
        DataFrame with added 'tier' column
    
    Example:
        >>> df = load_state_from_json('PA')
        >>> df = add_tier_column(df)
        >>> df[['county_name', 'swing_score', 'tier']].head()
    """
    df = df.copy()
    
    if score_col not in df.columns:
        raise ValueError(f"Column '{score_col}' not found in DataFrame")
    
    df['tier'] = df[score_col].apply(assign_tier)
    
    return df


def get_tier_summary(df: pd.DataFrame, tier_col: str = 'tier') -> pd.DataFrame:
    """
    Generate a summary of counties by tier.
    
    Args:
        df: DataFrame with tier column
        tier_col: Name of the tier column
    
    Returns:
        DataFrame with tier counts and percentages
    
    Example:
        >>> df = add_tier_column(load_state_from_json('PA'))
        >>> summary = get_tier_summary(df)
        >>> print(summary)
    """
    if tier_col not in df.columns:
        raise ValueError(f"Column '{tier_col}' not found in DataFrame")
    
    tier_counts = df[tier_col].value_counts()
    tier_percentages = (tier_counts / len(df) * 100).round(1)
    
    # Create summary with proper tier ordering (S, A, B, C, D)
    tier_order = ['S', 'A', 'B', 'C', 'D']
    
    summary_data = []
    for tier in tier_order:
        if tier in tier_counts.index:
            summary_data.append({
                'Tier': tier,
                'Count': tier_counts[tier],
                'Percentage': tier_percentages[tier],
                'Description': TIER_DESCRIPTIONS[tier],
                'Icon': TIER_EMOJIS[tier]
            })
    
    summary = pd.DataFrame(summary_data)
    
    return summary


def get_counties_by_tier(
    df: pd.DataFrame, 
    tier: str, 
    tier_col: str = 'tier',
    top_n: int = None
) -> pd.DataFrame:
    """
    Filter counties by tier classification.
    
    Args:
        df: DataFrame with tier column
        tier: Tier to filter (S, A, B, C, or D)
        tier_col: Name of the tier column
        top_n: Optional limit on number of counties to return
    
    Returns:
        DataFrame containing only counties in the specified tier
    
    Example:
        >>> df = add_tier_column(load_state_from_json('PA'))
        >>> s_tier = get_counties_by_tier(df, 'S')
        >>> print(f"Found {len(s_tier)} S-tier counties")
    """
    if tier_col not in df.columns:
        raise ValueError(f"Column '{tier_col}' not found in DataFrame")
    
    if tier not in TIER_THRESHOLDS:
        raise ValueError(f"Invalid tier '{tier}'. Must be one of: {list(TIER_THRESHOLDS.keys())}")
    
    filtered = df[df[tier_col] == tier].copy()
    
    if top_n is not None:
        filtered = filtered.head(top_n)
    
    return filtered


def get_tier_ranges() -> Dict[str, Tuple[float, float]]:
    """
    Get the score ranges for each tier.
    
    Returns:
        Dictionary mapping tier letters to (min, max) tuples
    
    Example:
        >>> ranges = get_tier_ranges()
        >>> print(f"S-tier range: {ranges['S']}")
    """
    return TIER_THRESHOLDS.copy()


def print_tier_guide():
    """
    Print a formatted guide explaining the tier system.
    
    Example:
        >>> print_tier_guide()
    """
    print("\n" + "="*80)
    print("SWING SCORE TIER SYSTEM")
    print("="*80)
    print("\nCounties are classified into 5 tiers based on their swing score (0-100%):\n")
    
    for tier in ['S', 'A', 'B', 'C', 'D']:
        min_score, max_score = TIER_THRESHOLDS[tier]
        emoji = TIER_EMOJIS[tier]
        desc = TIER_DESCRIPTIONS[tier]
        
        print(f"{emoji} Tier {tier}: {min_score*100:.0f}-{max_score*100:.0f}%")
        print(f"   {desc}\n")
    
    print("="*80 + "\n")


def export_tier_summary(
    df: pd.DataFrame,
    state_code: str,
    output_dir: str = "outputs"
) -> str:
    """
    Export a tier-based summary CSV for a state.
    
    Args:
        df: DataFrame with tier column
        state_code: Two-letter state code
        output_dir: Directory to save the output
    
    Returns:
        Path to the saved file
    
    Example:
        >>> df = add_tier_column(load_state_from_json('PA'))
        >>> path = export_tier_summary(df, 'PA')
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure we have the required columns
    cols_to_export = [
        'tier', 'county_name', 'county_fips', 'swing_score',
        'margin_change_abs', 'closeness_latest', 'turnout_latest'
    ]
    
    # Only include columns that exist
    cols_to_export = [c for c in cols_to_export if c in df.columns]
    
    # Add swing_score_100 if not present
    if 'swing_score_100' not in df.columns and 'swing_score' in df.columns:
        df['swing_score_100'] = (df['swing_score'] * 100).round(2)
        cols_to_export.insert(cols_to_export.index('swing_score') + 1, 'swing_score_100')
    
    export_df = df[cols_to_export].copy()
    
    # Sort by tier then by swing_score descending
    tier_order = ['S', 'A', 'B', 'C', 'D']
    export_df['tier_order'] = export_df['tier'].apply(lambda x: tier_order.index(x))
    export_df = export_df.sort_values(['tier_order', 'swing_score'], ascending=[True, False])
    export_df = export_df.drop('tier_order', axis=1)
    
    filename = f"{state_code}_tier_summary.csv"
    filepath = output_path / filename
    
    export_df.to_csv(filepath, index=False)
    
    print(f"✅ Exported tier summary to: {filepath}")
    print(f"   Total counties: {len(export_df)}")
    
    # Print tier breakdown
    tier_counts = export_df['tier'].value_counts().sort_index()
    for tier in tier_order:
        if tier in tier_counts.index:
            print(f"   {TIER_EMOJIS[tier]} Tier {tier}: {tier_counts[tier]} counties")
    
    return str(filepath)
