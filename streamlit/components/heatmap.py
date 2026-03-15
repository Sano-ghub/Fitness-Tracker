import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import calendar

# ── Color Maps ────────────────────────────────────────────────
STEPPER_COLORS = {
    "empty":   "#1a1a1a",
    "future":  "#2a2a2a",
    0:  "#7B1A1A",
    10: "#8B6914",
    20: "#4a7c3f",
    30: "#2d6e2d",
    40: "#1a5c1a",
}

VEGGIES_COLORS = {
    "empty":  "#7B1A1A",
    "future": "#2a2a2a",
    0: "#7B1A1A",
    1: "#1a5c1a",
}

JUNK_COLORS = {
    "empty":  "#7B1A1A",
    "future": "#2a2a2a",
    0: "#1a5c1a",
    1: "#4a7c3f",
    2: "#8B6914",
    3: "#7B1A1A",
}


def _stepper_color(row, today: date) -> str:
    d = row["date"]
    if d > today:
        return STEPPER_COLORS["future"]
    if row["weight_actual"] == "" and row["bf_done"] == "" and row["stepper_total"] == 0:
        return STEPPER_COLORS["empty"]
    mins = row["stepper_total"]
    if mins >= 40: return STEPPER_COLORS[40]
    if mins >= 30: return STEPPER_COLORS[30]
    if mins >= 20: return STEPPER_COLORS[20]
    if mins >= 10: return STEPPER_COLORS[10]
    return STEPPER_COLORS[0]


def _veggies_color(row, today: date) -> str:
    d = row["date"]
    if d > today:
        return VEGGIES_COLORS["future"]
    val = row.get("veggies_done", "")
    if val == "" or val is None:
        return VEGGIES_COLORS["empty"]
    return VEGGIES_COLORS[1] if str(val).upper() in ["TRUE", "1", "YES"] else VEGGIES_COLORS[0]


def _junk_color(row, today: date) -> str:
    d = row["date"]
    if d > today:
        return JUNK_COLORS["future"]
    val = row.get("junk_score", "")
    if val == "" or val is None:
        return JUNK_COLORS["empty"]
    return JUNK_COLORS.get(int(val), JUNK_COLORS["empty"])


import plotly.express as px
import numpy as np

def _build_heatmap(df: pd.DataFrame, year: int, month: int, color_fn, hover_fn, title: str) -> go.Figure:
    today = date.today()
    num_days     = calendar.monthrange(year, month)[1]
    first_day    = date(year, month, 1)
    first_weekday = first_day.weekday()
    days         = [date(year, month, d) for d in range(1, num_days + 1)]
    total_cells  = first_weekday + num_days
    num_weeks    = (total_cells + 6) // 7

    # 7 rows (Mon–Sun) x num_weeks cols
    color_grid = np.full((7, num_weeks), -1.0)   # -1 = empty cell
    hover_grid = [[""] * num_weeks for _ in range(7)]
    text_grid  = [[""] * num_weeks for _ in range(7)]

    for day_offset, d in enumerate(days):
        cell    = first_weekday + day_offset
        col_idx = cell // 7
        row_idx = cell % 7

        row_match = df[df["date"] == d]
        if row_match.empty:
            row_data = {"date": d, "weight_actual": "", "bf_done": "",
                        "stepper_total": 0, "veggies_done": "", "junk_score": ""}
        else:
            row_data = row_match.iloc[0]

        color_grid[row_idx][col_idx] = _color_to_value(color_fn(row_data, today), title)
        hover_grid[row_idx][col_idx] = hover_fn(row_data, d)
        text_grid[row_idx][col_idx]  = str(d.day)

    DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # build colorscale per heatmap type
    colorscale = _get_colorscale(title)

    fig = px.imshow(
        color_grid,
        color_continuous_scale=colorscale,
        zmin=0, zmax=3,
        aspect="equal",
    )

    fig.update_traces(
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_grid,
        xgap=4,
        ygap=4,
    )

    # day number annotations
    annotations = []
    for row_idx in range(7):
        for col_idx in range(num_weeks):
            if text_grid[row_idx][col_idx]:
                annotations.append(dict(
                    x=col_idx, y=row_idx,
                    text=text_grid[row_idx][col_idx],
                    showarrow=False,
                    font=dict(size=10, color="rgba(200,200,200,0.7)"),
                    xref="x", yref="y"
                ))

    fig.update_layout(
        annotations=annotations,
        title=dict(text=title, font=dict(size=13, color="#aaaaaa"), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis=dict(visible=False),
        yaxis=dict(
            tickvals=list(range(7)),
            ticktext=DAY_LABELS,
            tickfont=dict(size=11, color="#777"),
            showgrid=False,
            zeroline=False,
        ),
        margin=dict(t=30, b=10, l=45, r=10),
        height=260,
    )

    return fig


def _stepper_hover(row, d: date) -> str:
    total = row.get("stepper_total", 0) or 0
    return f"{d.strftime('%b %d')} — {int(total)} mins"


def _veggies_hover(row, d: date) -> str:
    val = row.get("veggies_done", "")
    status = "Yes" if str(val).upper() in ["TRUE", "1", "YES"] else "No"
    return f"{d.strftime('%b %d')} — Veggies: {status}"


def _junk_hover(row, d: date) -> str:
    from config import JUNK_SCORE_LABELS
    val = row.get("junk_score", "")
    label = JUNK_SCORE_LABELS.get(int(val), "No data") if val != "" else "No data"
    return f"{d.strftime('%b %d')} — Junk: {label}"


def render_heatmaps(df: pd.DataFrame):
    today = date.today()

    # month navigator in session state
    if "heatmap_year"  not in st.session_state:
        st.session_state.heatmap_year  = today.year
    if "heatmap_month" not in st.session_state:
        st.session_state.heatmap_month = today.month

    col_prev, col_title, col_next = st.columns([1, 4, 1])

    with col_prev:
        if st.button("◀", use_container_width=True):
            if st.session_state.heatmap_month == 1:
                st.session_state.heatmap_month = 12
                st.session_state.heatmap_year -= 1
            else:
                st.session_state.heatmap_month -= 1

    with col_title:
        st.markdown(
            f"<h4 style='text-align:center; margin:0;'>"
            f"{calendar.month_name[st.session_state.heatmap_month]} {st.session_state.heatmap_year}"
            f"</h4>",
            unsafe_allow_html=True
        )

    with col_next:
        if st.button("▶", use_container_width=True):
            if st.session_state.heatmap_month == 12:
                st.session_state.heatmap_month = 1
                st.session_state.heatmap_year += 1
            else:
                st.session_state.heatmap_month += 1

    # ── Prep df ───────────────────────────────────────────────
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date

    for col in ["bf_done", "lunch_done", "dinner_done", "intermediate_count"]:
        df[col] = df[col].replace("", 0)

    df["bf_done"]            = df["bf_done"].apply(lambda v: 1 if str(v).upper() in ["TRUE", "1"] else 0)
    df["lunch_done"]         = df["lunch_done"].apply(lambda v: 1 if str(v).upper() in ["TRUE", "1"] else 0)
    df["dinner_done"]        = df["dinner_done"].apply(lambda v: 1 if str(v).upper() in ["TRUE", "1"] else 0)
    df["intermediate_count"] = pd.to_numeric(df["intermediate_count"], errors="coerce").fillna(0)
    df["stepper_total"]      = (df["bf_done"] + df["lunch_done"] + df["dinner_done"] + df["intermediate_count"]) * 10

    y = st.session_state.heatmap_year
    m = st.session_state.heatmap_month

    st.plotly_chart(
        _build_heatmap(df, y, m, _stepper_color, _stepper_hover, "Stepper (mins)"),
        use_container_width=True, config={"displayModeBar": False}
    )
    st.plotly_chart(
        _build_heatmap(df, y, m, _veggies_color, _veggies_hover, "Veggies"),
        use_container_width=True, config={"displayModeBar": False}
    )
    st.plotly_chart(
        _build_heatmap(df, y, m, _junk_color, _junk_hover, "Junk Score"),
        use_container_width=True, config={"displayModeBar": False}
    )

def _color_to_value(color: str, title: str) -> float:
    """Map color string to numeric value for imshow z-grid."""
    if title == "Stepper (mins)":
        mapping = {
            STEPPER_COLORS["future"]: -1,
            STEPPER_COLORS[0]:  0,
            STEPPER_COLORS[10]: 1,
            STEPPER_COLORS[20]: 2,
            STEPPER_COLORS[30]: 3,
            STEPPER_COLORS[40]: 4,
        }
        return mapping.get(color, -1)

    elif title == "Veggies":
        return {
            VEGGIES_COLORS["future"]: -1,
            VEGGIES_COLORS[0]: 0,
            VEGGIES_COLORS[1]: 1,
        }.get(color, -1)

    elif title == "Junk Score":
        return {
            JUNK_COLORS["future"]: -1,
            JUNK_COLORS[0]: 0,
            JUNK_COLORS[1]: 1,
            JUNK_COLORS[2]: 2,
            JUNK_COLORS[3]: 3,
        }.get(color, -1)

    return -1


def _get_colorscale(title: str):
    if title == "Stepper (mins)":
        return [
            [0.0,  "#2a2a2a"],   # future/empty
            [0.25, "#7B1A1A"],   # 0 mins
            [0.5,  "#8B6914"],   # 10 mins
            [0.75, "#4a7c3f"],   # 20-30 mins
            [1.0,  "#1a5c1a"],   # 40 mins
        ]
    elif title == "Veggies":
        return [
            [0.0, "#2a2a2a"],
            [0.5, "#7B1A1A"],
            [1.0, "#1a5c1a"],
        ]
    elif title == "Junk Score":
        return [
            [0.0,  "#2a2a2a"],
            [0.33, "#1a5c1a"],
            [0.66, "#8B6914"],
            [1.0,  "#7B1A1A"],
        ]
    return [[0.0, "#2a2a2a"], [1.0, "#1a5c1a"]]