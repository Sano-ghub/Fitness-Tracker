# source/data_processor.py
from datetime import date, timedelta
from config import PHASES, STARTING_WEIGHT

def calculate_expected_weights():
    """
    Generates a dict of {date: expected_weight} for every day
    across all phases.
    """
    expected = {}
    phase_start_weight = STARTING_WEIGHT

    for phase in PHASES:
        start = phase["start"]
        end = phase["end"]
        total_days = (end - start).days + 1

        for day_offset in range(total_days):
            current_date = start + timedelta(days=day_offset)

            if phase["type"] == "loss":
                weeks = day_offset / 7
                weight = phase_start_weight * ((1 - phase["rate"]) ** weeks)

            elif phase["type"] == "gain":
                daily_gain = phase["flat_gain"] / ((end - start).days)
                weight = phase_start_weight + (daily_gain * day_offset)

            elif phase["type"] == "maintenance":
                weight = phase_start_weight

            expected[current_date] = round(weight, 2)

        # next phase starts from where this one ended
        phase_start_weight = expected[end]

    return expected

from datetime import date

def get_phase_remaining(phase: dict, today: date = None) -> dict:
    if today is None:
        today = date.today()
    
    days_remaining = (phase["end"] - today).days
    weeks_remaining = round(days_remaining / 7, 1)
    
    return {
        "days": max(0, days_remaining),
        "weeks": max(0, weeks_remaining)
    }