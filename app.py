import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
import io
from datetime import datetime, timedelta
import uuid
import plotly.express as px
import plotly.graph_objects as go
from pages.utils import (
    init_db, add_patient, get_queue, call_next, get_appointments,
    book_appointment, get_db_connection, validate_phone
)
from pages.ai_insights import (
    predict_eta, triage_score, get_doctor_availability, get_peak_hours,
    get_busiest_day, recommend_best_slot, get_chat_response
)

# ========================================
# Page Config & Init
# ========================================
st.set_page_config(page_title="ClinIQ", page_icon="hospital", layout="wide")
init_db()

st.sidebar.title("User Role")
role = st.sidebar.radio("Select Role", ["Patient", "Doctor", "Admin"], horizontal=True)

st.title("ClinIQ")
st.caption("AI-Powered Clinic Queue & Smart Scheduling System")

# ========================================
# PATIENT PORTAL
# ========================================
if role == "Patient":
    tab1, tab2, tab3, tab4 = st.tabs(["Check-in", "Track Queue", "Book Appointment", "AI Assistant"])

    # ------------------ CHECK-IN ------------------
    with tab1:
        st.subheader("Patient Check-in")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", key="cin_name")
            country = st.selectbox("Country", ["India", "Japan", "Other"], key="cin_country")
            hint = (
                "10 digits, start 6-9" if country == "India" else
                "10-11 digits, start 0" if country == "Japan" else
                "7-15 digits"
            )
            phone = st.text_input(f"Phone ({hint})", key="cin_phone")
        with col2:
            dept = st.selectbox("Department", ["General", "Cardiology", "Pediatrics", "Ortho"], key="cin_dept")
            symptoms = st.text_area("Symptoms (for AI Triage)", key="cin_symptoms")

        if st.button("Check-in Now", type="primary", key="cin_btn"):
            if not name.strip():
                st.error("Name is required."); st.stop()
            if not phone.strip():
                st.error("Phone is required."); st.stop()
            if not validate_phone(phone, country):
                st.error(f"Invalid phone for {country}. Please check format.")
                st.stop()
            if not dept:
                st.error("Please select a department."); st.stop()

            token = str(uuid.uuid4())[:8].upper()
            score = triage_score(symptoms)
            add_patient(name, phone, dept, token, score)
            st.success(f"Checked in! Token: **{token}**"); st.balloons()

            qr_data = f"TOKEN:{token}|NAME:{name}|DEPT:{dept}"
            qr = qrcode.make(qr_data)
            buf = io.BytesIO(); qr.save(buf, format="PNG"); buf.seek(0)
            st.image(buf, caption=f"Show at counter: {token}")

    # ------------------ TRACK QUEUE ------------------
    with tab2:
        st.subheader("Track Your Queue")
        token = st.text_input("Enter your Token", key="track_token")
        if st.button("Check Status", key="track_btn"):
            df = get_queue()
            user_row = df[df['token'] == token]
            if user_row.empty:
                st.error("Invalid token.")
            else:
                dept = user_row['dept'].iloc[0]
                dept_queue = df[df['dept'] == dept]
                pos = dept_queue[dept_queue['token'] == token].index[0] + 1
                eta = predict_eta(dept, pos)
                st.metric("Your Position", pos)
                st.metric("Est. Wait Time", f"{int(eta)} min")
                st.dataframe(dept_queue[['name', 'token', 'score']], hide_index=True)

    # ------------------ BOOK APPOINTMENT ------------------
    with tab3:
        st.subheader("Book Appointment")
        col1, col2 = st.columns(2)
        with col1:
            name_b = st.text_input("Full Name", key="bname")
            country_b = st.selectbox("Country", ["India", "Japan", "Other"], key="b_country")
            hint_b = (
                "10 digits, start 6-9" if country_b == "India" else
                "10-11 digits, start 0" if country_b == "Japan" else
                "7-15 digits"
            )
            phone_b = st.text_input(f"Phone ({hint_b})", key="bphone")
        with col2:
            dept_b = st.selectbox("Department", ["General", "Cardiology", "Pediatrics", "Ortho"], key="bdept")
            date_b = st.date_input("Date", min_value=datetime.today(), key="bdate")

        # Generate 30-min slots from 8 AM to 6 PM
        start_time = datetime.strptime("08:00", "%H:%M").time()
        end_time = datetime.strptime("18:00", "%H:%M").time()
        slots = []
        current = datetime.combine(date_b, start_time)
        while current.time() <= end_time:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)

        # Get booked slots
        conn = get_db_connection()
        booked_df = pd.read_sql(
            "SELECT slot FROM appointments WHERE dept=? AND substr(slot,1,10)=?",
            conn,
            params=(dept_b, date_b.strftime("%Y-%m-%d"))
        )
        conn.close()
        booked_times = {s.split(" ")[1][:5] for s in booked_df["slot"]}

        # Free slots
        free_slots = [s for s in slots if s not in booked_times]

        if not free_slots:
            st.warning("No slots available on this date. Try another day.")
            available = False
        else:
            available = True

        if available:
            chosen_time = st.selectbox("Available Time Slots", free_slots, key="btime")
        else:
            chosen_time = None

        if st.button("Book Selected Slot", type="primary", disabled=not available, key="book_btn"):
            if not name_b.strip():
                st.error("Name is required."); st.stop()
            if not phone_b.strip():
                st.error("Phone is required."); st.stop()
            if not validate_phone(phone_b, country_b):
                st.error(f"Invalid phone for {country_b}. Please check format.")
                st.stop()
            if not chosen_time:
                st.error("Please pick a time slot."); st.stop()

            slot = f"{date_b} {chosen_time}"
            if book_appointment(name_b, phone_b, dept_b, slot):
                st.success(f"Booked! **{dept_b}** on **{slot}**")
                rec = recommend_best_slot(dept_b)
                st.info(f"AI Tip: Best time to visit: **{rec}**")
            else:
                st.error("Slot already taken. Please choose another.")

    # ------------------ AI CHATBOT ------------------
    with tab4:
        st.subheader("AI Assistant")
        msg = st.text_input("Ask about queue, best time, etc.", key="chat_input")
        if st.button("Send", key="chat_send"):
            st.markdown(get_chat_response(msg))

# ========================================
# DOCTOR DASHBOARD
# ========================================
elif role == "Doctor":
    dept = st.selectbox("Your Department", ["General", "Cardiology", "Pediatrics", "Ortho"])
    queue = get_queue(dept=dept)
    appts = get_appointments(dept=dept)

    col1, col2, col3 = st.columns(3)
    col1.metric("Patients in Queue", len(queue))
    col2.metric("Today's Appointments", len(appts))
    avg_eta = predict_eta(dept, 1) if not queue.empty else 0
    col3.metric("Avg Wait Time", f"{int(avg_eta)} min")

    st.subheader("Call Next Patient")
    if st.button("CALL NEXT", type="primary", key="call_next"):
        call_next(dept)
        st.success("Patient called!")
        st.rerun()

    if not queue.empty:
        st.dataframe(queue[['name', 'token', 'score', 'arrival']], hide_index=True)
    else:
        st.info("No patients in queue.")

# ========================================
# ADMIN PANEL
# ========================================
elif role == "Admin":
    tab1, tab2, tab3 = st.tabs(["Live Queues", "AI Analytics", "Reports"])

    with tab1:
        st.subheader("Live Queue Status")
        for d in ["General", "Cardiology", "Pediatrics", "Ortho"]:
            q = len(get_queue(dept=d))
            st.metric(d, q)

    with tab2:
        st.subheader("AI-Powered Insights")
        avail = get_doctor_availability()
        best_hour = avail.idxmin()
        st.success(f"Most Available Hour: **{best_hour}:00**")
        busy_day = get_busiest_day()
        st.warning(f"Busiest Day: **{busy_day}**")
        fig = get_peak_hours()
        st.plotly_chart(fig, use_container_width=True)
        dept_sel = st.selectbox("Recommend for", ["General", "Cardiology", "Pediatrics", "Ortho"], key="rec_dept")
        rec = recommend_best_slot(dept_sel)
        st.info(f"AI Recommends: Book on **{rec}**")

    with tab3:
        st.subheader("Export Data")
        if st.button("Download Full Report (CSV)"):
            conn = get_db_connection()
            df = pd.read_sql("SELECT * FROM patients", conn)
            conn.close()
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "cliniq_report.csv", "text/csv")

st.markdown("---")
st.markdown("Built with Streamlit • AI-Powered • MIT License")