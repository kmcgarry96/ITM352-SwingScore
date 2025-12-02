"""
Data loading module for Swing County Calculator.

Handles reading raw election CSVs from the data/raw directory.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import glob
from .config import RAW_DATA_DIR, COLUMN_NAMES


def load_state_raw_data(state_code: str, data_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Load all raw CSV files for a given state from data/raw directory.
    
    Args:
        state_code: Two-letter state code (e.g., "AZ", "GA", "PA")
        data_dir: Override default raw data directory (optional)
    
    Returns:
        Combined DataFrame with all raw election data for the state
    
    Raises:
        FileNotFoundError: If no CSV files found for the state
        ValueError: If loaded data is empty or missing required columns
    
    Example:
        >>> df = load_state_raw_data("AZ")
        >>> df.shape
        (50000, 8)
    """
    # Use provided directory or default
    data_dir = data_dir or RAW_DATA_DIR
    state_upper = state_code.upper()
    state_lower = state_code.lower()
    
    # Look for CSV files matching state code (case-insensitive)
    # Patterns: AZ_*.csv, az_*.csv, 2020-az-*.csv, AZ-cleaned.csv, az22_cleaned.csv, etc.
    patterns = [
        f"{data_dir}/{state_upper}_*.csv",
        f"{data_dir}/{state_lower}_*.csv",
        f"{data_dir}/*-{state_lower}-*.csv",
        f"{data_dir}/*_{state_lower}_*.csv",
        f"{data_dir}/{state_upper}-*.csv",           # AZ-cleaned.csv
        f"{data_dir}/{state_lower}22_*.csv",         # az22_cleaned.csv
        f"{data_dir}/{state_upper.replace('NC', 'NC')}-*.csv"  # NC-cleaned-final3.csv
    ]
    
    # Find all matching files
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    if not files:
        raise FileNotFoundError(
            f"No CSV files found for state '{state_code}' in {data_dir}. "
            f"Expected files matching patterns: {patterns}"
        )
    
    print(f"Loading {len(files)} file(s) for {state_code}...")
    
    # Load and combine all CSVs
    dfs = []
    for file in files:
        print(f"  - {Path(file).name}")
        df = pd.read_csv(file)
        dfs.append(df)
    
    # Concatenate all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Add normalized state_code column if not present
    if 'state_code' not in combined_df.columns:
        # Try to extract from existing state column
        state_col = COLUMN_NAMES.get("state", "state_po")
        if state_col in combined_df.columns:
            combined_df['state_code'] = combined_df[state_col].str.upper()
        else:
            # Use the provided state_code
            combined_df['state_code'] = state_upper
    
    # Validate required columns exist
    required_cols = [
        COLUMN_NAMES["year"],
        COLUMN_NAMES["county_name"],
        COLUMN_NAMES["county_fips"],
        COLUMN_NAMES["party"],
        COLUMN_NAMES["votes"]
    ]
    
    missing_cols = [col for col in required_cols if col not in combined_df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns in {state_code} data: {missing_cols}. "
            f"Available columns: {list(combined_df.columns)}"
        )
    
    if combined_df.empty:
        raise ValueError(f"No data loaded for state '{state_code}'")
    
    print(f"✓ Loaded {len(combined_df):,} rows for {state_code}")
    
    return combined_df
