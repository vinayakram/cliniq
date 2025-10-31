import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
from pages.utils import get_db_connection

# Triage Scoring
def triage_score(symptoms):
    if not symptoms:
        return 1
    high = ['chest pain', 'bleeding', 'stroke', 'seizure', 'unconscious']
    med = ['fever', 'vomiting', 'severe pain', 'cough', 'headache']
    s = symptoms.lower()
    if any(x in s for x in high): return 5
    if any(x in s for x in med): return 3
    return 1

# ETA Prediction
def predict_eta(dept, position=1):
    conn = get_db_connection()
    df = pd.read_sql("SELECT service_start, service_end FROM patients WHERE service_end IS NOT NULL AND dept=?", conn, params=(dept,))
    conn.close()
    if df.empty:
        return 10 * position
    df['start'] = pd.to_datetime(df['service_start'])
    df['end'] = pd.to_datetime(df['service_end'])
    df['dur'] = (df['end'] - df['start']).dt.total_seconds() / 60
    avg = df['dur'].mean()
    return max(5, avg * position * np.random.uniform(0.9, 1.3))

# Most Available Hour
def get_doctor_availability():
    conn = get_db_connection()
    df = pd.read_sql("SELECT arrival FROM patients", conn)
    conn.close()
    if df.empty:
        return pd.Series(0, index=range(24))
    df['hour'] = pd.to_datetime(df['arrival']).dt.hour
    return df['hour'].value_counts().reindex(range(24), fill_value=0)

# Busiest Day
def get_busiest_day():
    conn = get_db_connection()
    df = pd.read_sql("SELECT arrival FROM patients", conn)
    conn.close()
    if df.empty:
        return "Monday"
    df['day'] = pd.to_datetime(df['arrival']).dt.day_name()
    return df['day'].value_counts().idxmax()

# Peak Hours Heatmap
def get_peak_hours():
    conn = get_db_connection()
    df = pd.read_sql("SELECT arrival, dept FROM patients", conn)
    conn.close()
    if df.empty:
        return px.bar(title="No Data Available")
    df['hour'] = pd.to_datetime(df['arrival']).dt.hour
    hm = df.groupby(['dept', 'hour']).size().reset_index(name='count')
    return px.density_heatmap(
        hm, x='hour', y='dept', z='count',
        color_continuous_scale="Reds",
        title="Patient Load Heatmap"
    )

# Recommend Best Slot
def recommend_best_slot(dept):
    avail = get_doctor_availability()
    best_hour = avail.idxmin()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    today = datetime.today().weekday()
    return f"{days[(today + 1) % 5]} at {best_hour}:00"

# Simple Chatbot
def get_chat_response(msg):
    msg = msg.lower()
    if "best time" in msg or "available" in msg:
        return f"Most available hour: **{get_doctor_availability().idxmin()}:00**"
    if "busy" in msg or "crowd" in msg:
        return f"Busiest day: **{get_busiest_day()}**"
    if "wait" in msg:
        return "Use the **Track Queue** tab with your token."
    if "book" in msg:
        return "Go to **Book Appointment** tab."
    return "How can I assist you? Try: best time, busy day, wait, book"