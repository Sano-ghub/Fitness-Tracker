# seed.py
import sys
sys.path.append("source")

from data_processor import calculate_expected_weights
from sheets_client import get_sheet
from config import SHEET_ID

def seed_sheet():
    sheet = get_sheet()
    expected_weights = calculate_expected_weights()

    headers = [
        "date", "weight_actual", "weight_expected",
        "bf_done", "lunch_done", "dinner_done",
        "intermediate_count", "veggies_done",
        "junk_score", "fast_24h", "notes"
    ]

    rows = []
    for date, weight in sorted(expected_weights.items()):
        row = [
            date.strftime("%Y-%m-%d"),
            "",
            weight,
            False,
            False,
            False,
            0,
            False,
            0,
            date.weekday() == 2,
            ""
        ]
        rows.append(row)
        print(f"Prepared row for {date}: {row}")

    sheet.clear()
    sheet.append_row(headers)
    sheet.append_rows(rows)  # single API call for all rows
    print(f"Seeded {len(rows)} rows successfully")

if __name__ == "__main__":
    seed_sheet()