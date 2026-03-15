import sys
sys.path.append("source")

import streamlit as st
from datetime import date

from tracker import get_latest_weight, get_phase_status, get_rolling_velocity, get_active_phase, get_sheet_as_df
from data_processor import get_phase_remaining
from components.gauges import render_phase_gauges

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="centered"
)

st.title("Progress")

# ── Data ─────────────────────────────────────────────────────
current_weight = get_latest_weight()
phases         = get_phase_status()
velocity       = get_rolling_velocity()
active_phase   = get_active_phase()

# ── Phase Gauges ─────────────────────────────────────────────
render_phase_gauges(phases, current_weight, velocity)

st.divider()

# ── Active Phase Info ─────────────────────────────────────────
if active_phase:
    remaining = get_phase_remaining(active_phase)

    st.caption(
        f"Currently in **{active_phase['name']}** — "
        f"ends {active_phase['end'].strftime('%b %d, %Y')}"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Weight",   f"{current_weight} kg")
    col2.metric("Days Remaining",   remaining["days"])
    col3.metric("Weeks Remaining",  remaining["weeks"])

else:
    st.caption("No active phase — between phases or journey complete.")

st.divider()

# ── Velocity ──────────────────────────────────────────────────
st.subheader("Velocity")

if velocity is not None:
    target_velocity = active_phase.get("rate", 0) * current_weight if active_phase else None

    v_col1, v_col2 = st.columns(2)
    v_col1.metric("Actual (7-day rolling)", f"{velocity} kg/wk")

    if target_velocity:
        delta = round(velocity - target_velocity, 2)
        v_col2.metric(
            "Target",
            f"{round(target_velocity, 2)} kg/wk",
            delta=f"{delta:+.2f} kg/wk",
            delta_color="normal"
        )
else:
    st.info("Not enough data yet for velocity — log at least 7 days to see this.")

from components.weight_chart import render_weight_chart

st.divider()
st.subheader("Weight")
df = get_sheet_as_df()
render_weight_chart(df)


from components.heatmap import render_heatmaps

st.divider()
st.subheader("Monthly Heatmaps")
render_heatmaps(df)