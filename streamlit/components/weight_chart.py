import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import date
from config import PHASES

THURSDAY_COLOR = "#E85D04"
ACTUAL_COLOR   = "#E0E0E0"
EXPECTED_COLOR = "#555555"
PHASE_LINE_COLOR = "#444444"


def _get_cutoff_date(df: pd.DataFrame) -> date:
    filled = df[df["weight_actual"] != ""].copy()
    if filled.empty:
        return date(2026, 3, 13)
    return pd.to_datetime(filled["date"]).max().date()


def _prepare_data(df: pd.DataFrame, cutoff: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df[df["date"] <= cutoff]

    actual_df = df[df["weight_actual"] != ""].copy()
    actual_df["weight_actual"] = pd.to_numeric(actual_df["weight_actual"], errors="coerce")
    actual_df = actual_df.dropna(subset=["weight_actual"])

    expected_df = df[df["weight_expected"] != ""].copy()
    expected_df["weight_expected"] = pd.to_numeric(expected_df["weight_expected"], errors="coerce")
    expected_df = expected_df.dropna(subset=["weight_expected"])

    return actual_df, expected_df


def _build_chart(actual_df: pd.DataFrame, expected_df: pd.DataFrame, start: date, end: date, show_phase_lines: bool) -> go.Figure:
    actual_df   = actual_df[(actual_df["date"] >= start) & (actual_df["date"] <= end)]
    expected_df = expected_df[(expected_df["date"] >= start) & (expected_df["date"] <= end)]

    fig = go.Figure()

    # ── Expected line (dotted ghost) ──────────────────────────
    fig.add_trace(go.Scatter(
        x=expected_df["date"],
        y=expected_df["weight_expected"],
        mode="lines",
        name="Expected",
        line=dict(color=EXPECTED_COLOR, dash="dot", width=1.5),
        hovertemplate="%{x}<br>Expected: %{y:.1f} kg<extra></extra>"
    ))

    # ── Actual line — normal days ─────────────────────────────
    normal_df   = actual_df[actual_df["date"].apply(lambda d: d.weekday() != 3)]
    thursday_df = actual_df[actual_df["date"].apply(lambda d: d.weekday() == 3)]

    fig.add_trace(go.Scatter(
        x=actual_df["date"],
        y=actual_df["weight_actual"],
        mode="lines",
        name="Actual",
        line=dict(color=ACTUAL_COLOR, width=2),
        showlegend=True,
        hovertemplate="%{x}<br>Actual: %{y:.1f} kg<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=normal_df["date"],
        y=normal_df["weight_actual"],
        mode="markers",
        name="Daily",
        marker=dict(color=ACTUAL_COLOR, size=5),
        showlegend=False,
        hovertemplate="%{x}<br>Actual: %{y:.1f} kg<extra></extra>"
    ))

    # ── Thursday markers ──────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=thursday_df["date"],
        y=thursday_df["weight_actual"],
        mode="markers",
        name="Thursday (post-fast)",
        marker=dict(color=THURSDAY_COLOR, size=8, symbol="diamond"),
        hovertemplate="%{x}<br>Thursday: %{y:.1f} kg<extra></extra>"
    ))

    # ── Phase boundary lines ──────────────────────────────────
    if show_phase_lines:
        display_phases = [p for p in PHASES if p.get("display", False)]
        for i, phase in enumerate(display_phases[:-1]):
            boundary = phase["end"]
            if start <= boundary <= end:
                fig.add_vline(
                    x=str(boundary),
                    line=dict(color=PHASE_LINE_COLOR, dash="dash", width=1),
                    annotation_text=f"{phase['name'].split(':')[1].strip()} ends",
                    annotation_position="top right",
                    annotation_font=dict(size=10, color=PHASE_LINE_COLOR)
                )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        xaxis=dict(
            gridcolor="#2a2a2a",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#2a2a2a",
            showgrid=True,
            zeroline=False,
            title="Weight (kg)"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11)
        ),
        hovermode="x unified",
        margin=dict(t=20, b=20, l=10, r=10),
        height=380,
    )

    return fig


def _build_weekly_chart(actual_df: pd.DataFrame, expected_df: pd.DataFrame, start: date, end: date) -> go.Figure:
    actual_df   = actual_df[(actual_df["date"] >= start) & (actual_df["date"] <= end)].copy()
    expected_df = expected_df[(expected_df["date"] >= start) & (expected_df["date"] <= end)].copy()

    actual_df["date"]   = pd.to_datetime(actual_df["date"])
    expected_df["date"] = pd.to_datetime(expected_df["date"])

    weekly_actual = (
        actual_df.set_index("date")["weight_actual"]
        .resample("W-MON")
        .mean()
        .dropna()
        .reset_index()
    )
    weekly_actual.columns = ["date", "weight_actual"]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=expected_df["date"],
        y=expected_df["weight_expected"],
        mode="lines",
        name="Expected",
        line=dict(color=EXPECTED_COLOR, dash="dot", width=1.5),
        hovertemplate="%{x|%b %d}<br>Expected: %{y:.1f} kg<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=weekly_actual["date"],
        y=weekly_actual["weight_actual"],
        mode="lines+markers",
        name="Weekly Avg",
        line=dict(color=ACTUAL_COLOR, width=2),
        marker=dict(color=ACTUAL_COLOR, size=7),
        hovertemplate="%{x|%b %d}<br>Weekly Avg: %{y:.1f} kg<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        xaxis=dict(gridcolor="#2a2a2a", showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="#2a2a2a", showgrid=True, zeroline=False, title="Weight (kg)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        hovermode="x unified",
        margin=dict(t=20, b=20, l=10, r=10),
        height=380,
    )

    return fig


def render_weight_chart(df: pd.DataFrame):
    cutoff = _get_cutoff_date(df)
    actual_df, expected_df = _prepare_data(df, cutoff)

    active_phase = next((p for p in PHASES if p.get("display") and p["start"] <= date.today() <= p["end"]), None)

    view = st.radio(
        "View",
        ["Current Phase", "Full Journey", "Weekly Avg"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if view == "Current Phase" and active_phase:
        start = active_phase["start"]
        end   = cutoff
        fig   = _build_chart(actual_df, expected_df, start, end, show_phase_lines=False)

    elif view == "Full Journey":
        start = date(2026, 3, 13)
        end   = cutoff
        fig   = _build_chart(actual_df, expected_df, start, end, show_phase_lines=True)

    else:  # Weekly Avg
        start = date(2026, 3, 13)
        end   = cutoff
        fig   = _build_weekly_chart(actual_df, expected_df, start, end)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})