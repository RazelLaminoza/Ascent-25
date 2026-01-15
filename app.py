import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
import time
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ASCENT APAC 2025",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STORAGE ----------------
DATA_FILE = "raffle_data.json"

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin" not in st.session_state:
    st.session_state.admin = False
if "entries" not in st.session_state:
    st.session_state.entries = []
if "winner" not in st.session_state:
    st.session_state.winner = None

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
        st.session_state.winner = data.get("winner", None)

# ---------------- HELPERS ----------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "entries": st.session_state.entries,
            "winner": st.session_state.winner
        }, f)

def generate_qr(data):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def landing_css(bg):
    with open(bg, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
    }}

    header, footer {{
        display: none !important;
    }}

    .hero {{
        width: 100vw;
        height: 100vh;
        background:
            linear-gradient(rgba(0,0,0,.65), rgba(0,0,0,.65)),
            url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}

    .hero-content {{
        color: white;
        max-width: 900px;
        padding: 30px;
    }}

    .hero-title {{
        font-size: clamp(2.8rem, 6vw, 5rem);
        font-weight: 900;
        letter-spacing: 3px;
    }}

    .hero-sub {{
        font-size: clamp(1.1rem, 2vw, 1.6rem);
        margin-top: 12px;
    }}

    .event {{
        margin-top: 26px;
        font-size: clamp(1rem, 1.5vw, 1.25rem);
        font-weight: 700;
        color: #FFD400;
        line-height: 1.6;
    }}

    .cta {{
        margin-top: 40px;
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- LANDING ----------------
if st.session_state.page == "landing":
    landing_css("bgna.png")

    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-title">ASCENT APAC 2025</div>
            <div class="hero-sub">
                Pre-register now and take part in the raffle
            </div>
            <div class="event">
                November 09, 2025<br>
                Okada Manila – Grand Ballroom<br>
                Entertainment City, Parañaque
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='cta'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Reminders"):
            st.info("Reminder feature coming soon")

    with c2:
        if st.button("Pre-Register"):
            st.session_state.page = "register"

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- REGISTRATION ----------------
elif st.session_state.page == "register":
    st.title("Event Registration")

    with st.form("register_form"):
        name = st.text_input("Full Name")
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")

        if submit:
            if not name or not emp:
                st.error("Please complete all fields")
            elif any(e["emp_number"] == emp for e in st.session_state.entries):
                st.warning("Employee already registered")
            else:
                st.session_state.entries.append({
                    "name": name,
                    "emp_number": emp
                })
                save_data()
                st.success("Registration successful!")
                qr = generate_qr(f"{name} | {emp}")
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="Your QR Code")

    if st.button("Admin Login"):
        st.session_state.page = "admin"

# ---------------- ADMIN LOGIN ----------------
elif st.session_state.page == "admin":
    st.title("Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == st.secrets["ADMIN_USER"] and p == st.secrets["ADMIN_PASS"]:
            st.session_state.admin = True
            st.session_state.page = "raffle"
        else:
            st.error("Invalid credentials")

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    st.title("🎉 Raffle Draw")

    if st.button("Logout"):
        st.session_state.admin = False
        st.session_state.page = "landing"

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        edited = st.data_editor(df, num_rows="dynamic")

        if st.button("Save Changes"):
            st.session_state.entries = edited.to_dict("records")
            save_data()

        if st.button("Run Raffle"):
            winner = random.choice(st.session_state.entries)
            st.session_state.winner = winner
            save_data()
            st.success(f"🎊 Winner: {winner['name']} ({winner['emp_number']})")
    else:
        st.info("No entries yet")
