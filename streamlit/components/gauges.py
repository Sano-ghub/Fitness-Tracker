import plotly.graph_objects as go
import streamlit as st

PHASE_COLORS = {
    "active": {
        0: {"ring": "#E85D04", "bg": "#370617"},
        1: {"ring": "#1A6B9A", "bg": "#03045E"},
        2: {"ring": "#B5A400", "bg": "#2D2A00"},
    },
    "locked":   {"ring": "#3a3a3a", "bg": "#1a1a1a"},
    "complete": {"ring": "#2D6A4F", "bg": "#1B4332"},
}


def _build_ring(phase: dict, index: int, current_weight: float, velocity: float | None) -> go.Figure:
    status = phase["status"]
    start  = phase["start_weight"] if "start_weight" in phase else phase["start"]
    end    = phase["end_weight"]   if "end_weight"   in phase else phase["end"]

    if status == "locked":
        colors      = PHASE_COLORS["locked"]
        center_text = f"{end} kg"
        sub_text    = f"{round(end - current_weight, 1)} kg gap"
        values      = [1]
        ring_colors = [colors["ring"]]
        pct         = 0

    elif status == "complete":
        colors      = PHASE_COLORS["complete"]
        center_text = "✓"
        sub_text    = "Complete"
        values      = [1]
        ring_colors = [colors["ring"]]
        pct         = 100

    else:  # active
        colors    = PHASE_COLORS["active"][index]
        total_gap = start - end
        progress  = max(0.0, min(1.0, (start - current_weight) / total_gap))
        remainder = 1.0 - progress
        pct       = round(progress * 100)
        center_text = f"{current_weight} kg"
        sub_text    = f"{round(current_weight - end, 1)} kg to go"
        values      = [progress, remainder]
        ring_colors = [colors["ring"], "#2a2a2a"]

    hover = (
        f"Progress: {pct}%<br>"
        f"Current: {current_weight} kg<br>"
        f"Target: {end} kg<br>"
        f"Velocity: {f'{velocity} kg/wk' if velocity is not None else '--'}"
    ) if status == "active" else ""

    fig = go.Figure(go.Pie(
        values=values,
        hole=0.72,
        marker=dict(colors=ring_colors, line=dict(width=0)),
        textinfo="none",
        hovertemplate=hover + "<extra></extra>",
        sort=False,
        direction="clockwise",
        rotation=90,
    ))

    fig.add_annotation(
        text=f"<b>{center_text}</b>",
        x=0.5, y=0.55,
        font=dict(size=16, color="#e0e0e0"),
        showarrow=False,
        xref="paper", yref="paper"
    )
    fig.add_annotation(
        text=sub_text,
        x=0.5, y=0.38,
        font=dict(size=11, color="#999999"),
        showarrow=False,
        xref="paper", yref="paper"
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor=colors["bg"],
        plot_bgcolor=colors["bg"],
        height=200,
    )

    return fig


def render_phase_gauges(phases: list[dict], current_weight: float, velocity: float | None):
    cols = st.columns(3)
    for i, (col, phase) in enumerate(zip(cols, phases)):
        fig = _build_ring(phase, i, current_weight, velocity)

        status_label = {
            "active":   "🟢 Active",
            "locked":   "🔒 Locked",
            "complete": "✅ Complete",
        }[phase["status"]]

        with col:
            st.caption(f"**{phase['name']}**")
            st.caption(status_label)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            if phase["status"] == "active":
                st.caption(f"Velocity: **{f'{velocity} kg/wk' if velocity is not None else '--'}**")
