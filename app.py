import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
import json
import os

st.set_page_config(
    page_title="ASCENT APAC 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    }}

    html, body {{
        overflow-x: hidden !important;
    }}

    ::-webkit-scrollbar {{
        display: none;
    }}

    #MainMenu, header, footer {{
        visibility: hidden;
    }}

    /* Make Streamlit crown almost invisible */
    [data-testid="stToolbar"] {{
        opacity: 0.04 !important;
        pointer-events: none !important;
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

    button[kind="primary"] {{
        background: white !important;
        color: black !important;
        border-radius: 30px;
        height: 55px;
        font-weight: 700;
    }}
    </style>
    """, unsafe_allow_html=True)


set_bg("bgna.png")

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":

    st.write("")  # spacing

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # IMAGE 1 (MAIN)
        st.image("1.png", use_column_width=True)

        st.markdown("""
        <p style="font-size:20px;font-weight:600;">
        PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
        <span style="font-size:16px;">
        January 25, 2026 | OKADA BALLROOM 1–3
        </span>
        </p>
        """, unsafe_allow_html=True)

        st.write("")  # spacing

        # IMAGE 2 (NORMAL, CENTERED, NO FLOAT)
        st.image("2.png", width=160)

    st.write("")

    colb1, colb2, colb3 = st.columns([2,1,2])
    with colb2:
        if st.button("Register", use_container_width=True):
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
