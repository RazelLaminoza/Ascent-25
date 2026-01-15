import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
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
if "show_form" not in st.session_state:
    st.session_state.show_form = False  # Controls overlay form

# Load saved data
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
        flex-direction: column;
        position: relative;
    }}

    .hero-content {{
        color: white;
        max-width: 900px;
        padding: 30px;
        z-index: 1;
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

    /* Yellow CTA button overlay */
    div.stButton > button {{
        background-color: #FFD400;
        color: black;
        font-weight: 800;
        padding: 14px 42px;
        border-radius: 40px;
        border: none;
        font-size: 18px;
        margin-top: 20px;
        z-index: 2;
    }}

    /* Overlay registration form modal */
    .overlay {{
        position: fixed;
        top:0;
        left:0;
        width:100%;
        height:100%;
        background: rgba(0,0,0,0.7);
        display:flex;
        justify-content:center;
        align-items:center;
        z-index: 999;
    }}

    .overlay-content {{
        background: rgba(255,255,255,0.95);
        padding: 30px;
        border-radius: 20px;
        width: 90%;
        max-width: 400px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }}

    </style>
    """, unsafe_allow_html=True)

# ---------------- LANDING ----------------
if st.session_state.page == "landing":
    landing_css("bgna.png")

    st.markdown(f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-title">ASCENT APAC 2025</div>
            <div class="hero-sub">Pre-register now and take part in the raffle</div>
            <div class="event">
                November 09, 2025<br>
                Okada Manila – Grand Ballroom<br>
                Entertainment City, Parañaque
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- PRE-REGISTER BUTTON ----------------
    center = st.columns([1,2,1])
    with center[1]:
        if st.button("Pre-Register"):
            st.session_state.show_form = True

    # ---------------- OVERLAY REGISTRATION FORM ----------------
    if st.session_state.show_form:
        st.markdown("""
        <div class="overlay">
            <div class="overlay-content">
                <h3>Register Now</h3>
        """, unsafe_allow_html=True)

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
                    st.session_state.entries.append({"name": name, "emp_number": emp})
                    save_data()
                    st.success("Registration successful!")
                    qr = generate_qr(f"{name} | {emp}")
                    buf = io.BytesIO()
                    qr.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="Your QR Code")
        
        # Close overlay div
        st.markdown("</div></div>", unsafe_allow_html=True)

    # ---------------- ADMIN LOGIN ----------------
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
