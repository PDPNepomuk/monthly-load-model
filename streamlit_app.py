
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import io

st.set_page_config(page_title="Monthly Electric Load Model", layout="wide")

st.title("⚡ Monthly Electric Load Model Generator")
st.markdown(
    """
A simple Streamlit app that creates an **hourly load profile for one month** based on:
- Operating hours
- Selected weekdays
- Base load and peak load (kW)
- Optional random variation for realism

Use the sidebar to set parameters, then generate and download the result as an Excel or CSV file.
"""
)

# --- Sidebar inputs ---
st.sidebar.header("Configuration")

col1, col2 = st.sidebar.columns(2)
with col1:
    year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.now().year, step=1)
with col2:
    month = st.number_input("Month (1-12)", min_value=1, max_value=12, value=datetime.now().month, step=1)

operating_start = st.sidebar.time_input("Operating start time", value=time(8,0))
operating_end = st.sidebar.time_input("Operating end time", value=time(18,0))

weekdays = st.sidebar.multiselect(
    "Operating days",
    options=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    default=["Monday","Tuesday","Wednesday","Thursday","Friday"]
)

base_load = st.sidebar.number_input("Base load (kW)", min_value=0.0, value=50.0, step=0.1, format="%.2f")
peak_load = st.sidebar.number_input("Peak load (kW)", min_value=0.0, value=150.0, step=0.1, format="%.2f")

random_pct = st.sidebar.slider("Random variation (% of instantaneous load)", min_value=0.0, max_value=30.0, value=5.0)
seed = st.sidebar.number_input("Random seed (0 = random)", min_value=0, value=0, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("Made for non-coders — copy the files to GitHub and deploy to Streamlit Community Cloud, or run locally with `streamlit run streamlit_app.py`.")

# --- Generate date range for the month ---
start_date = datetime(int(year), int(month), 1, 0, 0)
if month == 12:
    end_date = datetime(int(year) + 1, 1, 1) - timedelta(hours=1)
else:
    end_date = datetime(int(year), int(month) + 1, 1) - timedelta(hours=1)

date_range = pd.date_range(start=start_date, end=end_date, freq="H")

# --- Build load profile ---
rng = np.random.default_rng(None if seed == 0 else int(seed))

rows = []
for ts in date_range:
    dow = ts.strftime("%A")
    is_operating_day = dow in weekdays
    current_time = ts.time()

    # Check if within operating hours (inclusive start, exclusive end to avoid double-counting)
    in_hours = False
    if operating_start <= operating_end:
        in_hours = operating_start <= current_time < operating_end
    else:
        # overnight schedule (e.g., start 22:00 end 06:00)
        in_hours = (current_time >= operating_start) or (current_time < operating_end)

    if is_operating_day and in_hours:
        # Triangular profile peaking at midpoint of operating window
        start_seconds = operating_start.hour*3600 + operating_start.minute*60 + operating_start.second
        end_seconds = operating_end.hour*3600 + operating_end.minute*60 + operating_end.second
        # Handle overnight
        if end_seconds <= start_seconds:
            end_seconds += 24*3600
        current_seconds = ts.hour*3600 + ts.minute*60 + ts.second
        if current_seconds < start_seconds:
            current_seconds += 24*3600

        midpoint = (start_seconds + end_seconds) / 2.0
        if current_seconds <= midpoint:
            frac = (current_seconds - start_seconds) / max((midpoint - start_seconds), 1)
            load = base_load + (peak_load - base_load) * frac
        else:
            frac = (current_seconds - midpoint) / max((end_seconds - midpoint), 1)
            load = peak_load - (peak_load - base_load) * frac
    else:
        load = base_load

    # apply random variation (percentage of instantaneous load)
    if random_pct > 0:
        noise = rng.normal(loc=0.0, scale=random_pct/100.0) * load
        load = max(load + noise, 0)

    rows.append({
        "Datetime": ts,
        "Year": ts.year,
        "Month": ts.month,
        "Day": ts.day,
        "Hour": ts.hour,
        "Weekday": dow,
        "Operating": bool(is_operating_day and in_hours),
        "Load_kW": round(load, 3)
    })

df = pd.DataFrame(rows)

# --- Main UI: show charts and table ---
st.subheader("Preview — first 168 hours (1 week)")
st.dataframe(df.head(168))

st.subheader("Hourly load for the month")
chart = df.set_index("Datetime")["Load_kW"]
st.line_chart(chart)

st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Hours in month", int(len(df)))
col2.metric("Average load (kW)", f"{df['Load_kW'].mean():.2f}")
col3.metric("Peak load (kW)", f"{df['Load_kW'].max():.2f}")

# --- Download buttons ---
def to_excel_bytes(dataframe: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="LoadModel")
        writer.save()
    buffer.seek(0)
    return buffer.read()

def to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Excel (.xlsx)",
    data=to_excel_bytes(df),
    file_name=f"load_model_{int(year)}_{int(month):02d}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button(
    "📥 Download CSV",
    data=to_csv_bytes(df),
    file_name=f"load_model_{int(year)}_{int(month):02d}.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("If you want help publishing this to **Streamlit Community Cloud**, follow the README included with this project or ask me to walk you through each step and I'll do it for you.")
