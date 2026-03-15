from datetime import date

STARTING_WEIGHT = 106.0

PHASES = [
    {
        "name": "Phase 1: The Sprint",
        "start": date(2026, 3, 13),
        "end": date(2026, 5, 15),
        "rate": 0.012,
        "type": "loss",
        "start_weight": 106.0,
        "end_weight": 95.1,
        "display": True
    },
    {
        "name": "Vacation Buffer",
        "start": date(2026, 5, 16),
        "end": date(2026, 5, 30),
        "rate": 0.0,
        "type": "gain",
        "flat_gain": 1.5
    },
    {
        "name": "Phase 2: The Cruise",
        "start": date(2026, 6, 1),
        "end": date(2026, 8, 31),
        "rate": 0.010,
        "type": "loss",
        "start_weight": 96.59,
        "end_weight": 84.76,
        "display": True
    },
    {
        "name": "Refeed",
        "start": date(2026, 9, 1),
        "end": date(2026, 9, 7),
        "rate": 0.0,
        "type": "maintenance"
    },
    {
        "name": "Phase 3: The Finish",
        "start": date(2026, 9, 8),
        "end": date(2026, 12, 15),
        "rate": 0.008,
        "type": "loss",
        "start_weight": 84.76,
        "end_weight": 75.75,
        "display": True
    },
]

SHEET_NAME = "Fitness Tracker"

SHEET_ID = "1rNouOjBfXhypt3MoVsmMqQHj96WL8gS-picSYm28vgc"

JUNK_SCORE_LABELS = {
    0: "Clean",
    1: "Light",
    2: "Moderate",
    3: "Heavy"
}

STEPPER_MINS_PER_SESSION = 10