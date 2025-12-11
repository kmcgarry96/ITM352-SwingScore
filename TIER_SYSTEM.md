# Swing Score Tier System

The tier system classifies counties into 5 categories (S, A, B, C, D) based on their swing scores to help prioritize campaign resources and identify high-value targets.

## Tier Classifications

| Tier | Score Range | Icon | Description | Strategy |
|------|-------------|------|-------------|----------|
| **S** | 70-100% | 🏆 | **Elite** - Unicorn counties with exceptional scores across all metrics | Maximum investment - these are the crown jewels |
| **A** | 55-70% | ⭐ | **Excellent** - Top priority targets with strong swing potential | Heavy investment - primary focus areas |
| **B** | 40-55% | ✅ | **Good** - Solid swing counties worth significant investment | Moderate-to-heavy investment |
| **C** | 25-40% | 📊 | **Moderate** - Secondary targets for remaining resources | Light-to-moderate investment |
| **D** | 0-25% | 📉 | **Low Priority** - Limited swing potential or low competitiveness | Minimal investment |

## Key Findings

Across all 7 swing states (AZ, GA, MI, NC, NV, PA, WI):
- **511 total counties** analyzed
- **Only 5 counties (1.0%)** achieved S-tier status
- **8 counties (1.6%)** in A-tier
- **30 counties (5.9%)** in B-tier
- **Top score: 76.2%** (Maricopa County, AZ)

## The Elite Five (S-Tier Counties)

These are the only 5 counties across all swing states that scored above 70%:

1. 🏆 **MARICOPA, AZ** - 76.2%
2. 🏆 **CLARK, NV** - 75.4%
3. 🏆 **FULTON, GA** - 72.8%
4. 🏆 **ALLEGHENY, PA** - 72.0%
5. 🏆 **MECKLENBURG, NC** - 71.2%

These counties excel across all four swing score components:
- High margin change (significant swing between elections)
- High closeness (extremely competitive races)
- High turnout (engaged electorate)
- Large population (high vote counts)

## Why No County Scores Near 100%

The swing score is a weighted average of four normalized components. To score near 100%, a county would need to:
- Have the **largest margin swing** in the dataset
- Be the **most competitive** (closest to 50-50)
- Have the **highest turnout**
- Be the **largest county** by population

This combination is extremely rare because:
- Large counties tend to be politically stable (lower margin swings)
- Very competitive counties often have moderate swings
- High-turnout areas may not be as competitive

**Result**: Even elite S-tier counties typically max out around 75%, making them genuinely rare and valuable targets.

## Usage Examples

### View tier system guide
```bash
python3 -m backend.tier_analysis --guide
```

### Analyze all states
```bash
python3 -m backend.tier_analysis
```

### Analyze specific state
```bash
python3 -m backend.tier_analysis PA
```

### Show only S-tier counties across all states
```bash
python3 -m backend.tier_analysis --tier S
```

### Show A-tier counties in Pennsylvania
```bash
python3 -m backend.tier_analysis PA --tier A
```

### Export tier summary CSVs for all states
```bash
python3 -m backend.tier_analysis --export
```

## Tier Distribution by State

| State | S | A | B | C | D | Total |
|-------|---|---|---|---|---|-------|
| AZ    | 1 | 0 | 0 | 9 | 5 | 15    |
| GA    | 1 | 2 | 12| 41| 103| 159  |
| MI    | 0 | 2 | 2 | 25| 52 | 81   |
| NC    | 1 | 1 | 2 | 55| 41 | 100  |
| NV    | 1 | 0 | 0 | 7 | 9 | 17    |
| PA    | 1 | 2 | 8 | 14| 42 | 67   |
| WI    | 0 | 1 | 6 | 21| 44 | 72   |

## Output Files

Tier summary CSV files are exported to `outputs/` directory:
- `AZ_tier_summary.csv`
- `GA_tier_summary.csv`
- `MI_tier_summary.csv`
- `NC_tier_summary.csv`
- `NV_tier_summary.csv`
- `PA_tier_summary.csv`
- `WI_tier_summary.csv`

Each CSV contains:
- `tier` - S, A, B, C, or D classification
- `county_name` - County name
- `county_fips` - 5-digit FIPS code
- `swing_score` - Raw score (0-1)
- `swing_score_100` - Percentage score (0-100)
- `margin_change_abs` - Absolute margin change
- `closeness_latest` - Competitiveness score
- `turnout_latest` - Voter turnout proxy

Counties are sorted by tier (S to D), then by score within each tier.

## Integration with Existing Tools

The tier system works alongside your existing tools:
- Use with `export_top_counties.py` to focus on specific tiers
- Integrate into Flask app for tier-based filtering
- Combine with interactive maps to visualize tiers geographically

## For Your Presentation

**Key Talking Points:**
1. Only 1% of counties achieve elite (S-tier) status - truly rare targets
2. The tier system makes resource allocation concrete and actionable
3. Geographic concentration: Each swing state has at most 1-2 S-tier counties
4. S+A tiers combined = just 2.6% of counties but highest ROI for campaigns
5. The mathematical reality: No perfect 100% county exists because the metrics trade off against each other
