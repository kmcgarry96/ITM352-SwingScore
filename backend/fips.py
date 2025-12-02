from typing import Any
import pandas as pd


def format_fips(value: Any) -> str:
    """Normalize a county FIPS value to a zero-padded 5-digit string.

    Handles numeric values (int/float), numeric strings ("13121" or "13121.0"),
    and returns an empty string for missing/NA values.
    """
    try:
        if pd.isna(value):
            return ""
    except Exception:
        # If pandas isn't available or pd.isna errors, continue
        pass

    try:
        # Convert floats like 13121.0 or ints to int first, then format
        iv = int(float(value))
        return f"{iv:05d}"
    except Exception:
        # Fallback: coerce to str, strip whitespace, and if it contains a decimal
        # part remove it. Otherwise, zero-pad if it's all digits and shorter than 5.
        s = str(value).strip()
        if '.' in s:
            s = s.split('.')[0]
        if s.isdigit():
            return s.zfill(5)
        return s
