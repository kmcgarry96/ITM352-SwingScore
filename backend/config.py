"""
Configuration constants for Swing County Calculator backend.

This file defines all configurable parameters including:
- Data directory paths
- Column name mappings
- Party label definitions
- Default election years
- Swing score component weights
"""

# =============================================================================
# DATA DIRECTORIES
# =============================================================================

RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"

# =============================================================================
# DEFAULT SETTINGS
# =============================================================================

# States to process (edit this list as needed)
DEFAULT_STATES = ["AZ", "GA", "MI", "NC", "NV", "PA", "WI"]

# Default election years for comparison
DEFAULT_YEAR_PREV = 2020
DEFAULT_YEAR_LATEST = 2022

# =============================================================================
# COLUMN NAME MAPPINGS
# =============================================================================
# Maps expected column names to actual column names in your raw CSVs.
# Edit these if your CSV columns are named differently.

COLUMN_NAMES = {
    "year": "year",
    "state": "state_po",  # or "state" depending on your CSV
    "county_name": "county_name",
    "county_fips": "county_fips",
    "party": "party_simplified",
    "votes": "votes"
}

# =============================================================================
# PARTY LABEL MAPPINGS
# =============================================================================
# Define which party labels in your data map to DEM, REP, OTHER.
# These are lists to handle variations (e.g., "DEMOCRAT" vs "DEM").

PARTY_LABELS = {
    "dem": ["DEMOCRAT", "DEM", "Democratic"],
    "rep": ["REPUBLICAN", "REP", "Republican"],
    "other": ["OTHER", "LIBERTARIAN", "GREEN", "INDEPENDENT"]
}

# =============================================================================
# SWING SCORE WEIGHTS
# =============================================================================
# Weights for the four swing score components (must sum to 1.0).
# Adjust these to change how each factor influences the final swing score.

SWING_WEIGHTS = {
    "margin_change": 0.25,   # How much the margin shifted between elections
    "closeness": 0.25,        # How close the latest election was
    "turnout": 0.25,          # Voter turnout (using total votes as proxy)
    "votes": 0.25             # County size/population weight
}

# Validate weights sum to 1.0
assert abs(sum(SWING_WEIGHTS.values()) - 1.0) < 0.001, \
    "SWING_WEIGHTS must sum to 1.0"
