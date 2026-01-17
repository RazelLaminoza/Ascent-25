import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
import time
import json
import os

# ---------------- STORAGE FILE ----------------
DATA_FILE = "raffle_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
        st.session_state.winner = data.get("winner", None)
else:
    st.session_state.entries = []
    st.session_state.winner = None

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin" not in st.session_state:
    st.session_state.admin = False

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

def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    html, body {{
        overflow: hidden !important;
    }}

    ::-webkit-scrollbar {{
        display: none;
    }}

    #MainMenu, header, footer {{
        visibility: hidden;
    }}

    h1, h2, h3 {{
        color: white;
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
    }}

    /* FORM CONTAINER */
    .stForm {{
        background: rgba(0, 0, 0, 0.25) !important;
        padding: 25px !important;
        border-radius: 18px !important;
        backdrop-filter: blur(8px);
    }}

    /* 🔴 RED INPUTS (NORMAL) */
    .stTextInput > div > div > input,
    .stTextInput > div > div > textarea {{
        background: rgba(255, 0, 0, 0.25) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px !important;
    }}

    /* 🔴 RED INPUTS (FOCUS / TYPING) */
    .stTextInput input:focus,
    .stTextInput textarea:focus {{
        background: rgba(255, 0, 0, 0.4) !important;
        outline: none !important;
        color: white !important;
    }}

    /* 🔴 CHROME AUTOFILL FIX */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus {{
        -webkit-box-shadow: 0 0 0 1000px rgba(255, 0, 0, 0.4) inset !important;
        -webkit-text-fill-color: white !important;
    }}

    /* 🔴 ADMIN INPUT FIX */
    div[data-testid="stTextInput"] > div > input {{
        background: rgba(255, 0, 0, 0.25) !important;
        color: white !important;
    }}

    /* BUTTONS */
    button[kind="primary"] {{
        background-color: #FFD000 !important;
        color: black !important;
        border-radius: 30px !important;
        height: 55px;
        font-size: 18px;
        font-weight: 700;
        border: none;
    }}

    button[kind="primary"]:hover {{
        background-color: #FFB700 !important;
    }}

    .fixed-logo {{
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
    }}

    @media (max-width: 768px) {{
        html, body {{ overflow-y: auto !important; }}
        button {{ width: 100% !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg_local("bgna.png")

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown('<div class="fixed-logo">', unsafe_allow_html=True)
    st.image("2.png", width=160)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.image("1.png", use_column_width=True)

    colb1, colb2, colb3 = st.columns([2,1,2])
    with colb2:
        if st.button("Register", use_container_width=True):
            st.session_state.page = "register"

# ---------------- REGISTRATION PAGE ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)

    with st.form("register_form"):
        name = st.text_input("Full Name")
        emp_number = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")

        if submit:
            if name and emp_number:
                if any(e["emp_number"] == emp_number for e in st.session_state.entries):
                    st.warning("Employee ID already registered")
                else:
                    st.session_state.entries.append({"name": name, "emp_number": emp_number})
                    save_data()
                    st.success("Registration successful!")
                    qr = generate_qr(f"{name} | {emp_number}")
                    buf = io.BytesIO()
                    qr.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="Your QR Code")
            else:
                st.error("Please complete all fields")

    if not st.session_state.admin:
        if st.button("Admin Login"):
            st.session_state.page = "admin"

# ---------------- ADMIN LOGIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h2>Admin Login</h2>", unsafe_allow_html=True)
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back"):
            st.session_state.page = "register"
    with col2:
        if st.button("Login"):
            if user == st.secrets["ADMIN_USER"] and pwd == st.secrets["ADMIN_PASS"]:
                st.session_state.admin = True
                st.session_state.page = "raffle"
            else:
                st.error("Invalid credentials")

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    if st.button("🚪 Logout Admin"):
        st.session_state.admin = False
        st.session_state.page = "landing"

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        edited_df = st.data_editor(df, num_rows="dynamic")

        if st.button("Save Table Changes"):
            st.session_state.entries = edited_df.to_dict("records")
            save_data()
            st.success("Saved!")

        if st.button("Run Raffle"):
            winner = random.choice(st.session_state.entries)
            st.markdown(
                f"<h1 style='color:#FFD700;font-size:80px'>{winner['name']} ({winner['emp_number']})</h1>",
                unsafe_allow_html=True
            )
    else:
        st.info("No registrations yet")
