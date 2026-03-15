# source/tracker.py
import pandas as pd
from datetime import date
from sheets_client import get_sheet

from config import PHASES
from datetime import date

def get_row_for_date(target_date: date) -> dict:
    """Fetch a single row for a given date. Returns empty dict if not found."""
    sheet = get_sheet()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    
    date_str = target_date.strftime("%Y-%m-%d")
    row = df[df["date"] == date_str]
    
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def upsert_row(target_date: date, data: dict):
    """Update the existing row for a given date."""
    sheet = get_sheet()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    
    date_str = target_date.strftime("%Y-%m-%d")
    row_index = df[df["date"] == date_str].index

    if row_index.empty:
        return False  # date not in sheet, shouldn't happen after seeding

    # +2 because gspread is 1-indexed and row 1 is headers
    sheet_row = row_index[0] + 2

    col_map = {col: idx + 1 for idx, col in enumerate(df.columns)}

    for field, value in data.items():
        if field in col_map:
            sheet.update_cell(sheet_row, col_map[field], value)

    return True

def get_latest_weight() -> float:
    sheet = get_sheet()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    # filter rows where weight_actual is not empty
    filled = df[df["weight_actual"] != ""]

    if filled.empty:
        return 106.0  # fallback to starting weight if nothing logged yet

    # return the most recent entry
    return float(filled.iloc[-1]["weight_actual"])

def get_active_phase(today: date = None) -> dict | None:
    if today is None:
        today = date.today()
    
    for phase in PHASES:
        if phase["start"] <= today <= phase["end"]:
            return phase
    return None

def get_phase_status(today: date = None) -> list[dict]:
    if today is None:
        today = date.today()

    result = []
    for phase in PHASES:
        if not phase.get("display", False):
            continue
        if today < phase["start"]:
            status = "locked"
        elif today > phase["end"]:
            status = "complete"
        else:
            status = "active"
        result.append({**phase, "status": status})
    return result


def get_rolling_velocity() -> float | None:
    sheet = get_sheet()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    # keep only rows with actual weight logged
    df = df[df["weight_actual"] != ""].copy()
    df["weight_actual"] = pd.to_numeric(df["weight_actual"], errors="coerce")
    df = df.dropna(subset=["weight_actual"])
    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 7:
        return None

    current_window = df.tail(7)["weight_actual"].mean()

    # use whatever is available before the last 7 days
    previous_df = df.iloc[:-7]
    if previous_df.empty:
        return None
    
    previous_window = previous_df.tail(7)["weight_actual"].mean()

    velocity = round(previous_window - current_window, 2)
    return velocity

def get_sheet_as_df() -> pd.DataFrame:
    sheet = get_sheet()
    return pd.DataFrame(sheet.get_all_records())