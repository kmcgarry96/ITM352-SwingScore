# SwingScoreBackend — Quick README

This project computes "swing scores" for counties in major swing states and exports ranked lists useful for analysis or canvassing.

Quick status
- The repository includes precomputed county-level swing scores in `swingscorejsons/swing_scores_all_states.json`.
- I added CLI tools that load that JSON, compute (or recompute) final scores from normalized components, and export ranked CSVs to `outputs/`.
- **NEW**: Tier system (S, A, B, C, D) classifies counties by swing potential - see [TIER_SYSTEM.md](TIER_SYSTEM.md) for details.

Setup (one-time)
1. Create & activate the virtual environment (macOS/Linux zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2. Install requirements:
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Run the exporter
- Export top-20 counties for the default swing states (AZ, GA, MI, NC, NV, PA, WI):
```bash
python -m backend.export_top_counties --top 20
```
- Export top-20 using only the two primary components (closeness, margin shift) with equal weights:
```bash
python -m backend.export_top_counties --top 20 --weights 0.5,0.5
```
- Export using four-component weights (margin_change, closeness, turnout, votes):
```bash
python -m backend.export_top_counties --top 20 --weights 0.25,0.25,0.25,0.25
```

Outputs
- CSV files are written to `outputs/` (e.g. `outputs/PA_top20.csv`). Each CSV includes these columns:
  - `county_name`, `county_fips` (zero-padded 5-digit string), `swing_score_100`, `margin_change_pct`, `latest_abs_margin_pct`, `turnout_latest` (and `impact_score` = swing_score_100 × turnout_latest)

Notes for plotting with Plotly (optional)
- To map scores to counties you will need a county GeoJSON whose feature ids are 5-digit FIPS codes (Census provides these). The CSV `county_fips` column is zero-padded and ready to join.
- A minimal example (once `plotly` is installed):
```python
import plotly.express as px
import pandas as pd
geojson = 'counties.geojson'  # county GeoJSON file
df = pd.read_csv('outputs/PA_top20.csv')
fig = px.choropleth(df, geojson=geojson, locations='county_fips', color='swing_score_100',
                    color_continuous_scale='RdYlBu', scope='usa')
fig.write_html('pa_swing_map.html')
```

If you want, I can add a ready-to-run Plotly example that downloads the GeoJSON and produces an HTML map for one state.

## Tier System (NEW!)

Counties are classified into 5 tiers based on swing scores:
- 🏆 **S-tier (70-100%)**: Elite unicorn counties - only 5 exist across all swing states!
- ⭐ **A-tier (55-70%)**: Excellent top priority targets
- ✅ **B-tier (40-55%)**: Good solid swing counties
- 📊 **C-tier (25-40%)**: Moderate secondary targets
- 📉 **D-tier (0-25%)**: Low priority

**Usage:**
```bash
# View tier system guide
python3 -m backend.tier_analysis --guide

# Analyze all states with tier breakdown
python3 -m backend.tier_analysis

# Analyze specific state
python3 -m backend.tier_analysis PA

# Show only S-tier counties
python3 -m backend.tier_analysis --tier S

# Export tier summaries to CSV
python3 -m backend.tier_analysis --export
```

**The Elite Five (S-tier counties):**
1. 🏆 MARICOPA, AZ (76.2%)
2. 🏆 CLARK, NV (75.4%)
3. 🏆 FULTON, GA (72.8%)
4. 🏆 ALLEGHENY, PA (72.0%)
5. 🏆 MECKLENBURG, NC (71.2%)

See [TIER_SYSTEM.md](TIER_SYSTEM.md) for full documentation.

## Web Interface

Run the Flask web UI to explore swing scores interactively:
```bash
python3 -m backend.app
```
Then open `http://127.0.0.1:5000/` in your browser.

Questions / next steps
- Tier system implemented! Use it to prioritize campaign resources.
- Flask web UI available for interactive exploration.
