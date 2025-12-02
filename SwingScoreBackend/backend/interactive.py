"""Simple interactive CLI to explore swing scores by state.

Features:
- Prompts the user to enter a two-letter state code (defaults to PA if blank)
- Displays a top-N table of counties by swing score
- Offers to generate an interactive Plotly map (uses backend.plotly_map)

Run:
    python -m backend.interactive
"""
from pathlib import Path
import sys

import pandas as pd

try:
    from tabulate import tabulate
except Exception:
    tabulate = None

from backend.json_loader import load_state_from_json
from backend import config


def prompt_state() -> str:
    choices = ','.join(config.DEFAULT_STATES)
    prompt = f"Enter one of the states ({choices}) [default PA]: "
    s = input(prompt).strip()
    if not s:
        return 'PA'
    return s.upper()


def show_top_counties(df: pd.DataFrame, top: int | str = 10):
    if df.empty:
        print('No data to show.')
        return

    # Ensure numeric swing_score_100
    if 'swing_score_100' not in df.columns:
        if 'swing_score' in df.columns:
            df['swing_score_100'] = (df['swing_score'].astype(float) * 100).round(2)
        else:
            df['swing_score_100'] = 0.0

    disp = df[['county_name', 'county_fips', 'swing_score_100', 'margin_change_abs', 'closeness_latest', 'turnout_latest']].copy()

    # Accept 'all' or 0 to show full dataset
    if isinstance(top, str) and top.strip().lower() == 'all':
        top_n = len(disp)
    else:
        try:
            top_n = int(top)
            if top_n <= 0:
                top_n = len(disp)
        except Exception:
            top_n = 10

    disp = disp.head(top_n)
    # prettier county names
    disp['county_name'] = disp['county_name'].str.title()

    print('\nTop counties by swing score:\n')
    if tabulate:
        table = tabulate(disp.values, headers=disp.columns, tablefmt='github', showindex=range(1, len(disp) + 1))
        print(table)
    else:
        # fallback: pandas pretty print
        print(disp.to_string(index=False))


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    yn = 'Y/n' if default else 'y/N'
    resp = input(f"{prompt} ({yn}): ").strip().lower()
    if resp == '':
        return default
    return resp[0] == 'y'


def main():
    print('Swing Score Explorer — interactive')
    state = prompt_state()
    df = load_state_from_json(state)
    if df.empty:
        print(f'No data found for state: {state}')
        sys.exit(1)

    # Ask how many rows to show
    try:
        top_n = int(input('How many top counties to show? [default 10]: ').strip() or '10')
    except ValueError:
        top_n = 10

    show_top_counties(df, top=top_n)

    if ask_yes_no('Generate an interactive Plotly map for this state?', default=False):
        # Save a CSV and call the plotly_map.make_map function
        out_csv = Path('outputs') / f"{state}_interactive.csv"
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)

        try:
            from backend.plotly_map import make_map
            out_file = make_map(state, out_csv, Path('outputs'))
            print('Map written to:', out_file)
            if ask_yes_no('Open the map in your default browser now?', default=True):
                # macOS open
                import webbrowser
                webbrowser.open(out_file.resolve().as_uri())
        except Exception as e:
            print('Failed to create map:', e)


if __name__ == '__main__':
    main()
