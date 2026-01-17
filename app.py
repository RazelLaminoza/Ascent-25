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
    page_title="ASCENT APAC 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STORAGE ----------------
DATA_FILE = "raffle_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
else:
    st.session_state.entries = []

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin" not in st.session_state:
    st.session_state.admin = False

# ---------------- FUNCTIONS ----------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"entries": st.session_state.entries}, f)

def generate_qr(data):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def set_bg(image):
    with open(image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        height: 100vh;
        overflow: hidden !important;
    }}

    html, body {{
        height: 100vh;
        overflow: hidden !important;
        margin: 0;
    }}

    ::-webkit-scrollbar {{
        display: none !important;
    }}

    #MainMenu, header, footer {{
        visibility: hidden !important;
        height: 0px !important;
    }}

    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    [data-testid="stDecoration"],
    svg[aria-label="Streamlit"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }}

    h1, p {{
        color: white;
        text-align: center;
        text-shadow: 1px 1px 4px rgba(0,0,0,.7);
    }}

    .stTextInput input {{
        background: rgba(255,255,255,0.12) !important;
        border-radius: 12px;
        border: none;
        color: red !important;
        caret-color: red !important;
    }}

    div.stButton > button:first-child {{
        background: white !important;
        color: black !important;
        border-radius: 30px;
        height: 55px;
        font-weight: 700;
        padding: 0 40px;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown(
        f"""
        <div style='height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;'>
            <img src='data:image/png;base64,{base64.b64encode(open("2.png","rb").read()).decode()}' width='160' style='margin-bottom:20px;'/>
            <img src='data:image/png;base64,{base64.b64encode(open("1.png","rb").read()).decode()}' style='width:70%; max-width:900px; margin-bottom:20px;'/>
            <p style="font-size:20px;font-weight:600; color:white; text-shadow:1px 1px 4px rgba(0,0,0,.7); margin-bottom:30px;">
                PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
                <span style="font-size:16px;">
                January 25, 2026 | OKADA BALLROOM 1–3
                </span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([5,1,5])
    with col2:
        if st.button("Register"):
            st.session_state.page = "register"

# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)

    with st.form("form"):
        name = st.text_input("Full Name")
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")

        if submit:
            if name and emp:
                if any(e["emp"] == emp for e in st.session_state.entries):
                    st.warning("Employee ID already registered")
                else:
                    st.session_state.entries.append({"name": name, "emp": emp})
                    save_data()
                    st.success("Registered!")
                    qr = generate_qr(f"{name} | {emp}")
                    buf = io.BytesIO()
                    qr.save(buf, format="PNG")
                    st.image(buf.getvalue())
            else:
                st.error("Complete all fields")

    if st.button("Admin Login"):
        st.session_state.page = "admin"

# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == st.secrets["ADMIN_USER"] and pwd == st.secrets["ADMIN_PASS"]:
            st.session_state.admin = True
            st.session_state.page = "raffle"
        else:
            st.error("Invalid login")

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        st.data_editor(df)

        if st.button("Run Raffle"):
            winner = random.choice(st.session_state.entries)
            st.markdown(
                f"<h1 style='color:gold;font-size:80px'>{winner['name']}</h1>",
                unsafe_allow_html=True
            )
    else:
        st.info("No registrations yet")
