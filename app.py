import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
import json
import os
from PIL import Image, ImageDraw, ImageFont

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
if "winner" not in st.session_state:
    st.session_state.winner = None

# ---------------- FUNCTIONS ----------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"entries": st.session_state.entries}, f)

def generate_qr(data):
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def create_pass_image(emp, qr_img):
    img = Image.new("RGB", (900, 500), "#ff4b5c")
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 42)
        font_small = ImageFont.truetype("arial.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    draw.text((40, 40), "ASCENT APAC 2026", fill="white", font=font_big)
    draw.text((40, 140), f"EMPLOYEE NO:", fill="white", font=font_small)
    draw.text((40, 180), emp, fill="white", font=font_big)

    draw.text(
        (40, 260),
        "Present this pre-registration pass\nat the check-in counter",
        fill="white",
        font=font_small
    )

    qr_img = qr_img.resize((220, 220))
    img.paste(qr_img, (620, 140))

    return img

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
    }}
    #MainMenu, header, footer {{
        visibility: hidden;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

# ---------------- NAV ----------------
def go_to(page):
    st.session_state.page = page

# ---------------- LANDING ----------------
if st.session_state.page == "landing":
    st.markdown(
        """
        <div style="height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;">
            <h1>ASCENT APAC 2026</h1>
            <p>January 25, 2026 | OKADA BALLROOM 1–3</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("Register", on_click=go_to, args=("register",))

# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register</h1>", unsafe_allow_html=True)

    with st.form("register_form"):
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Generate Pass")

    if submit:
        if not emp:
            st.error("Please enter Employee ID")
        elif any(e["emp"] == emp for e in st.session_state.entries):
            st.warning("Employee ID already registered")
        else:
            st.session_state.entries.append({"emp": emp})
            save_data()

            qr_img = generate_qr(emp)
            pass_img = create_pass_image(emp, qr_img)

            buf = io.BytesIO()
            pass_img.save(buf, format="PNG")
            pass_bytes = buf.getvalue()

            st.success("Registration successful!")

            st.image(pass_bytes, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "📥 Download Pass (PNG)",
                    pass_bytes,
                    file_name=f"{emp}_event_pass.png",
                    mime="image/png"
                )

            with col2:
                st.markdown(
                    """
                    <button onclick="window.print()"
                    style="
                        width:100%;
                        height:48px;
                        border-radius:24px;
                        border:none;
                        background:black;
                        color:white;
                        font-size:16px;
                        cursor:pointer;">
                        🖨 Print Pass
                    </button>
                    """,
                    unsafe_allow_html=True
                )

    st.button("Admin Login", on_click=go_to, args=("admin",))

# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    st.text_input("Username", key="user")
    st.text_input("Password", type="password", key="pwd")

    if st.button("Login"):
        if (
            st.session_state.user == st.secrets["ADMIN_USER"]
            and st.session_state.pwd == st.secrets["ADMIN_PASS"]
        ):
            st.session_state.admin = True
            go_to("raffle")
        else:
            st.error("Invalid login")

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.entries)
    st.data_editor(df)

    if st.button("Run Raffle"):
        st.session_state.winner = random.choice(st.session_state.entries)

    if st.session_state.winner:
        st.markdown(
            f"<h1 style='color:gold;font-size:80px'>{st.session_state.winner['emp']}</h1>",
            unsafe_allow_html=True
        )

    st.button("Logout", on_click=go_to, args=("landing",))
