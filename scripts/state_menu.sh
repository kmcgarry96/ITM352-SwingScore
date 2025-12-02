#!/usr/bin/env bash
# Simple state picker wrapper that calls the Python backend scripts for you.
# Usage: ./scripts/state_menu.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$ROOT_DIR/.venv/bin/python"

STATES=(AZ GA MI NC NV PA WI)

echo "Pick a swing state to inspect:"
PS3="Enter number (or q to quit): "
select st in "${STATES[@]}"; do
    if [[ -z "$st" ]]; then
        echo "Invalid selection. Try again or press Ctrl-C to exit."
        continue
    fi
    STATE="$st"
    echo "You picked: $STATE"
    break
done

OUT_CSV="$ROOT_DIR/outputs/${STATE}_interactive.csv"
echo "Exporting full county CSV for $STATE -> $OUT_CSV"
"$VENV_PY" -m backend.export_full_state --state "$STATE" --out "$OUT_CSV"

echo
echo "Showing top 20 counties from $OUT_CSV (selected columns)"
# Use Python to print a clean table of selected columns (falls back to head if python fails)
if "$VENV_PY" -c "import pandas as pd,sys; df=pd.read_csv('$OUT_CSV', dtype={'county_fips':str}); df['county_fips']=df['county_fips'].apply(lambda x: str(x).zfill(5));
cols=['county_name','county_fips','swing_score','margin_change_abs','closeness_latest','turnout_latest'];
df2 = df[ [c for c in cols if c in df.columns] ].copy();
if 'swing_score' in df2.columns: df2['swing_score'] = (df2['swing_score'].astype(float)*100).round(2);
print(df2.head(20).to_string(index=False))"; then
    true
else
    head -n 21 "$OUT_CSV" || true
fi

read -rp "Generate interactive Plotly map for $STATE now? (y/N): " genmap
    genmap=${genmap:-n}
    genmap_lc=$(echo "$genmap" | tr '[:upper:]' '[:lower:]')
    if [[ "$genmap_lc" == "y" ]]; then
    echo "Generating map..."
    "$VENV_PY" -m backend.plotly_map --state "$STATE" --input "$OUT_CSV" --out "$ROOT_DIR/outputs"
    echo "Map written to: $ROOT_DIR/outputs/${STATE}_swing_map.html"
    read -rp "Open the map in your default browser now? (Y/n): " openmap
        openmap=${openmap:-y}
        openmap_lc=$(echo "$openmap" | tr '[:upper:]' '[:lower:]')
        if [[ "$openmap_lc" == "y" ]]; then
        # macOS open
        open "$ROOT_DIR/outputs/${STATE}_swing_map.html" || true
    fi
fi

echo "Done."
