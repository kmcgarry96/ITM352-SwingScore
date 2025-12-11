#!/usr/bin/env python3
"""
Interactive tier analysis tool for swing score data.

Usage:
    python -m backend.tier_analysis             # Analyze all states
    python -m backend.tier_analysis PA          # Analyze single state
    python -m backend.tier_analysis PA --tier S # Show only S-tier counties
"""

import argparse
from pathlib import Path
import sys

from backend.json_loader import load_state_from_json
from backend.tier_system import (
    add_tier_column,
    get_tier_summary,
    get_counties_by_tier,
    print_tier_guide,
    export_tier_summary,
    TIER_EMOJIS
)
from backend.config import DEFAULT_STATES


def analyze_state(state_code: str, tier_filter: str = None, export: bool = False):
    """Analyze swing scores for a single state with tier classification."""
    
    print(f"\n{'='*80}")
    print(f"SWING SCORE TIER ANALYSIS - {state_code}")
    print(f"{'='*80}\n")
    
    # Load data
    df = load_state_from_json(state_code)
    
    if df.empty:
        print(f"❌ No data found for state: {state_code}")
        return
    
    # Add tier classification
    df = add_tier_column(df)
    
    # Add swing_score_100 for display
    if 'swing_score_100' not in df.columns:
        df['swing_score_100'] = (df['swing_score'] * 100).round(2)
    
    print(f"📊 Total counties analyzed: {len(df)}")
    print(f"📈 Score range: {df['swing_score_100'].min():.1f} - {df['swing_score_100'].max():.1f}")
    print(f"📉 Average score: {df['swing_score_100'].mean():.1f}")
    
    # Show tier summary
    print(f"\n{'─'*80}")
    print("TIER DISTRIBUTION")
    print(f"{'─'*80}\n")
    
    tier_summary = get_tier_summary(df)
    for _, row in tier_summary.iterrows():
        print(f"{row['Icon']} Tier {row['Tier']}: {row['Count']:2d} counties ({row['Percentage']:5.1f}%)")
        print(f"   {row['Description']}")
        print()
    
    # If tier filter specified, show those counties
    if tier_filter:
        print(f"\n{'─'*80}")
        print(f"{TIER_EMOJIS[tier_filter]} TIER {tier_filter} COUNTIES")
        print(f"{'─'*80}\n")
        
        tier_df = get_counties_by_tier(df, tier_filter)
        
        if tier_df.empty:
            print(f"No Tier {tier_filter} counties found in {state_code}")
        else:
            # Display top counties
            display_cols = ['county_name', 'swing_score_100', 'tier']
            if 'margin_change_abs' in tier_df.columns:
                display_cols.append('margin_change_abs')
            if 'closeness_latest' in tier_df.columns:
                display_cols.append('closeness_latest')
            
            for i, row in tier_df.iterrows():
                print(f"{i+1:2d}. {row['county_name']:<30} Score: {row['swing_score_100']:5.1f}")
                if 'margin_change_abs' in row:
                    print(f"     Margin Change: {row['margin_change_abs']*100:5.2f}%  ", end="")
                if 'closeness_latest' in row:
                    print(f"Closeness: {row['closeness_latest']*100:5.1f}%")
                else:
                    print()
    else:
        # Show top 10 overall
        print(f"\n{'─'*80}")
        print(f"TOP 10 COUNTIES (All Tiers)")
        print(f"{'─'*80}\n")
        
        top_10 = df.nlargest(10, 'swing_score_100')
        for idx, (i, row) in enumerate(top_10.iterrows(), 1):
            emoji = TIER_EMOJIS[row['tier']]
            print(f"{idx:2d}. {emoji} {row['county_name']:<25} Tier {row['tier']}  Score: {row['swing_score_100']:5.1f}")
    
    # Export if requested
    if export:
        print(f"\n{'─'*80}")
        export_tier_summary(df, state_code)
    
    print()


def analyze_all_states(tier_filter: str = None, export: bool = False):
    """Analyze all default swing states."""
    
    print_tier_guide()
    
    all_data = []
    
    for state in DEFAULT_STATES:
        df = load_state_from_json(state)
        if not df.empty:
            df = add_tier_column(df)
            df['state'] = state
            all_data.append(df)
    
    if not all_data:
        print("❌ No data found for any states")
        return
    
    import pandas as pd
    combined = pd.concat(all_data, ignore_index=True)
    
    if 'swing_score_100' not in combined.columns:
        combined['swing_score_100'] = (combined['swing_score'] * 100).round(2)
    
    print(f"\n{'='*80}")
    print(f"CROSS-STATE TIER ANALYSIS")
    print(f"{'='*80}\n")
    
    print(f"📊 Total counties across {len(DEFAULT_STATES)} states: {len(combined)}")
    print(f"📈 Score range: {combined['swing_score_100'].min():.1f} - {combined['swing_score_100'].max():.1f}")
    print(f"📉 Average score: {combined['swing_score_100'].mean():.1f}\n")
    
    # Overall tier distribution
    tier_summary = get_tier_summary(combined)
    print(f"{'─'*80}")
    print("OVERALL TIER DISTRIBUTION")
    print(f"{'─'*80}\n")
    
    for _, row in tier_summary.iterrows():
        print(f"{row['Icon']} Tier {row['Tier']}: {row['Count']:3d} counties ({row['Percentage']:5.1f}%)")
    
    # Tier distribution by state
    print(f"\n{'─'*80}")
    print("TIER DISTRIBUTION BY STATE")
    print(f"{'─'*80}\n")
    
    pivot = pd.crosstab(combined['state'], combined['tier'], margins=True)
    # Reorder columns to S, A, B, C, D
    tier_order = [t for t in ['S', 'A', 'B', 'C', 'D'] if t in pivot.columns]
    pivot = pivot[tier_order + ['All']]
    print(pivot.to_string())
    
    # Top counties across all states
    if tier_filter:
        print(f"\n{'─'*80}")
        print(f"{TIER_EMOJIS[tier_filter]} TOP TIER {tier_filter} COUNTIES (ALL STATES)")
        print(f"{'─'*80}\n")
        
        tier_df = get_counties_by_tier(combined, tier_filter)
        tier_df = tier_df.nlargest(20, 'swing_score_100')
        
        for idx, (i, row) in enumerate(tier_df.iterrows(), 1):
            print(f"{idx:2d}. {row['state']} - {row['county_name']:<25} Score: {row['swing_score_100']:5.1f}")
    else:
        print(f"\n{'─'*80}")
        print(f"🏆 TOP 20 COUNTIES (ALL STATES)")
        print(f"{'─'*80}\n")
        
        top_20 = combined.nlargest(20, 'swing_score_100')
        
        for idx, (i, row) in enumerate(top_20.iterrows(), 1):
            emoji = TIER_EMOJIS[row['tier']]
            print(f"{idx:2d}. {emoji} {row['state']} - {row['county_name']:<20} Tier {row['tier']}  Score: {row['swing_score_100']:5.1f}")
    
    # Export if requested
    if export:
        print(f"\n{'─'*80}")
        for state in DEFAULT_STATES:
            state_df = combined[combined['state'] == state]
            if not state_df.empty:
                export_tier_summary(state_df, state)
    
    print()


def main():
    """Main entry point for tier analysis tool."""
    
    parser = argparse.ArgumentParser(
        description='Analyze swing scores with tier classifications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend.tier_analysis              # Analyze all states
  python -m backend.tier_analysis PA           # Analyze Pennsylvania
  python -m backend.tier_analysis PA --tier S  # Show S-tier counties in PA
  python -m backend.tier_analysis --export     # Export tier summaries
  python -m backend.tier_analysis --guide      # Show tier system guide
        """
    )
    
    parser.add_argument(
        'state',
        nargs='?',
        help='State code to analyze (e.g., PA, GA). If omitted, analyzes all states.'
    )
    
    parser.add_argument(
        '--tier',
        choices=['S', 'A', 'B', 'C', 'D'],
        help='Filter to show only counties in specific tier'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export tier summary CSV files to outputs/'
    )
    
    parser.add_argument(
        '--guide',
        action='store_true',
        help='Print tier system guide and exit'
    )
    
    args = parser.parse_args()
    
    if args.guide:
        print_tier_guide()
        return
    
    if args.state:
        analyze_state(args.state.upper(), args.tier, args.export)
    else:
        analyze_all_states(args.tier, args.export)


if __name__ == '__main__':
    main()
