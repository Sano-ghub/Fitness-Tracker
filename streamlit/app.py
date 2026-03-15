import sys

sys.path.append("source")

import streamlit as st
from datetime import date
from tracker import get_row_for_date, upsert_row
from config import JUNK_SCORE_LABELS
from utils import to_bool

st.set_page_config(
    page_title="Fitness Tracker",
    page_icon="💪",
    layout="centered"  # keeps it narrow and mobile friendly
)

st.title("Daily Log")

# ── Date Picker ──────────────────────────────────────────────
selected_date = st.date_input("Date", value=date.today())

# ── Fetch existing row for selected date ─────────────────────
row = get_row_for_date(selected_date)

if row:
    st.caption("✏️ Editing existing entry for this date")
else:
    st.caption("🆕 No entry found for this date")

st.divider()

# ── Weight ───────────────────────────────────────────────────
weight = st.number_input(
    "Weight (kg)",
    min_value=0.0,
    max_value=300.0,
    value=float(row.get("weight_actual", 0.0) or 0.0),
    step=0.1,
    format="%.1f"
)

st.divider()

# ── Stepper Sessions ─────────────────────────────────────────
st.subheader("Stepper Sessions")
bf_done = st.checkbox("After Breakfast", value=to_bool(row.get("bf_done", False)))
lunch_done = st.checkbox("After Lunch", value=to_bool(row.get("lunch_done", False)))
dinner_done = st.checkbox("After Dinner", value=to_bool(row.get("dinner_done", False)))

st.write("Intermediate Sessions")
intermediate_count = st.number_input(
    "Count",
    min_value=0,
    max_value=20,
    value=int(row.get("intermediate_count", 0) or 0),
    step=1
)

total_mins = (bf_done + lunch_done + dinner_done + intermediate_count) * 10
st.info(f"Total stepper time today: **{total_mins} mins**")

st.divider()

# ── Veggies ──────────────────────────────────────────────────
veggies_done = st.checkbox(
    "Veggies done today?",
    value=to_bool(row.get("veggies_done", False))
)

st.divider()

# ── Junk Score ───────────────────────────────────────────────
st.subheader("Junk Score")
junk_score = st.select_slider(
    "How clean was today?",
    options=[0, 1, 2, 3],
    value=int(row.get("junk_score", 0) or 0),
    format_func=lambda x: f"{x} — {JUNK_SCORE_LABELS[x]}"
)

st.divider()

# ── Fasting ──────────────────────────────────────────────────
if selected_date.weekday() == 2:  # Wednesday
    st.info("⚡ Fasting day — automatically marked")

st.divider()

# ── Notes ────────────────────────────────────────────────────
notes = st.text_area(
    "Notes",
    value=row.get("notes", "") or "",
    placeholder="Leg day, felt groggy, skipped morning walk..."
)

st.divider()

# ── Submit ───────────────────────────────────────────────────
if st.button("Save Entry", use_container_width=True, type="primary"):
    data = {
        "weight_actual": weight,
        "bf_done": bf_done,
        "lunch_done": lunch_done,
        "dinner_done": dinner_done,
        "intermediate_count": intermediate_count,
        "veggies_done": veggies_done,
        "junk_score": junk_score,
        "fast_24h": selected_date.weekday() == 2,
        "notes": notes
    }

    success = upsert_row(selected_date, data)

    if success:
        st.success(f"✅ Logged for {selected_date.strftime('%b %d, %Y')}")
    else:
        st.error("❌ Date not found in sheet — make sure seed has been run")