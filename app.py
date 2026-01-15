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

# ---------------- STORAGE FILE ----------------
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

# Load saved data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
        st.session_state.winner = data.get("winner", None)

# ---------------- FUNCTIONS ----------------
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

def fullscreen_landing_css(bg):
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
        visibility: hidden;
        height: 0px;
    }}

    .landing {{
        width: 100vw;
        height: 100vh;
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .overlay {{
        background: rgba(0,0,0,0.6);
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}

    .content {{
        color: white;
        max-width: 900px;
        padding: 20px;
    }}

    .title {{
        font-size: clamp(2.5rem, 6vw, 5rem);
        font-weight: 900;
        letter-spacing: 2px;
    }}

    .subtitle {{
        font-size: clamp(1rem, 2vw, 1.5rem);
        margin-top: 10px;
    }}

    .event {{
        margin-top: 25px;
        font-size: clamp(0.9rem, 1.5vw, 1.2rem);
        color: #FFD400;
        font-weight: 600;
    }}

    .buttons {{
        margin-top: 40px;
        display: flex;
        gap: 20px;
        justify-content: center;
        flex-wrap: wrap;
    }}

    .btn {{
        padding: 14px 38px;
        border-radius: 30px;
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        border: none;
    }}

    .primary {{
        background: #FFD400;
        color: black;
    }}

    .outline {{
        background: transparent;
        border: 2px solid white;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    fullscreen_landing_css("bgna.png")

    st.markdown("""
    <div class="landing">
        <div class="overlay">
            <div class="content">
                <div class="title">ASCENT APAC 2025</div>
                <div class="subtitle">
                    Pre-register now and take part in the raffle
                </div>

                <div class="event">
                    November 09, 2025<br>
                    Okada Manila – Grand Ballroom<br>
                    Entertainment City, Parañaque
                </div>

                <div class="buttons">
                    <form>
                        <button class="btn outline">Reminders</button>
                        <button class="btn primary">Pre-Register</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Pre-Register", key="go_register"):
            st.session_state.page = "register"
    with col2:
        if st.button("Reminders", key="go_reminder"):
            st.info("Reminder feature coming soon")

# ---------------- REGISTRATION PAGE ----------------
elif st.session_state.page == "register":
    st.title("Event Registration")

    with st.form("register"):
        name = st.text_input("Full Name")
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")

        if submit:
            if not name or not emp:
                st.error("Please complete all fields")
            elif any(e["emp_number"] == emp for e in st.session_state.entries):
                st.warning("Employee already registered")
            else:
                st.session_state.entries.append({"name": name, "emp_number": emp})
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

# ---------------- RAFFLE PAGE ----------------
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
