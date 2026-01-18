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
EMPLOYEE_FILE = "employees.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        st.session_state.entries = json.load(f).get("entries", [])
else:
    st.session_state.entries = []

if os.path.exists(EMPLOYEE_FILE):
    with open(EMPLOYEE_FILE, "r") as f:
        st.session_state.valid_employees = json.load(f)
else:
    st.session_state.valid_employees = {}

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

def save_employees():
    with open(EMPLOYEE_FILE, "w") as f:
        json.dump(st.session_state.valid_employees, f)

def generate_qr(data):
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def create_pass_image(name, emp, qr_img):
    bg = Image.open("bgna.png").convert("RGBA").resize((900, 500))
    img = Image.new("RGBA", (900, 500))
    img.paste(bg, (0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("CourierPrime-Bold.ttf", 42)
        font_small = ImageFont.truetype("CourierPrime-Bold.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    text_color = (255, 255, 255, 255)

    # --- LOGOS (NO STRETCH) ---
    logo1 = Image.open("1.png").convert("RGBA")
    logo2 = Image.open("2.png").convert("RGBA")
    logo1.thumbnail((120, 120), Image.LANCZOS)
    logo2.thumbnail((120, 120), Image.LANCZOS)

    img.paste(logo1, (620, 30), logo1)
    img.paste(logo2, (760, 30), logo2)

    draw.text((40, 40), "ASCENT APAC 2026", fill=text_color, font=font_big)
    draw.text((40, 120), "FULL NAME:", fill=text_color, font=font_big)
    draw.text((40, 160), name, fill=text_color, font=font_small)
    draw.text((40, 260), "EMPLOYEE NO:", fill=text_color, font=font_small)
    draw.text((40, 300), emp, fill=text_color, font=font_big)

    draw.text(
        (40, 380),
        "Present this pre-registration pass\nat the check-in counter",
        fill=text_color,
        font=font_small
    )

    qr_img = qr_img.resize((220, 220))
    img.paste(qr_img, (620, 140), qr_img.convert("RGBA"))

    return img.convert("RGB")

# ---------------- STYLE ----------------
def set_bg(image):
    encoded = base64.b64encode(open(image, "rb").read()).decode()
    st.markdown(f"""
    <style>
    html, body {{
        height:100vh;
        overflow:hidden;
        margin:0;
    }}
    [data-testid="stAppViewContainer"] {{
        background-image:url("data:image/png;base64,{encoded}");
        background-size:cover;
        background-position:center;
        height:100vh;
        overflow:hidden;
    }}
    #MainMenu, header, footer {{
        visibility:hidden;
        height:0;
    }}
    button {{
        min-height:56px;
        font-size:20px;
        padding:14px 36px;
        border-radius:30px;
        margin:10px auto;
        display:block;
    }}
    button[kind="primary"] {{
        background:#FFD400 !important;
        color:black !important;
        font-weight:800;
    }}
    button[kind="secondary"] {{
        background:black !important;
        color:white !important;
    }}
    h1,p {{
        color:white;
        text-align:center;
        text-shadow:1px 1px 4px rgba(0,0,0,.7);
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

# ---------------- NAV ----------------
def go_to(p): st.session_state.page = p

def login_admin():
    if st.session_state.user == st.secrets["ADMIN_USER"] and st.session_state.pwd == st.secrets["ADMIN_PASS"]:
        st.session_state.admin = True
        st.session_state.page = "raffle"
    else:
        st.session_state.login_error = True

def run_raffle():
    if st.session_state.entries:
        st.session_state.winner = random.choice(st.session_state.entries)

def logout():
    st.session_state.admin = False
    st.session_state.page = "landing"
    st.session_state.winner = None

def delete_all():
    st.session_state.entries = []
    save_data()
    st.session_state.winner = None

def export_csv():
    pd.DataFrame(st.session_state.entries).to_csv("entries.csv", index=False)
    st.session_state.exported = True

# ---------------- LANDING ----------------
if st.session_state.page == "landing":
    st.markdown(f"""
    <div style="height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;">
        <img src="data:image/png;base64,{base64.b64encode(open('2.png','rb').read()).decode()}" width="160">
        <img src="data:image/png;base64,{base64.b64encode(open('1.png','rb').read()).decode()}"
             style="width:70%;max-width:900px;margin-top:20px;">
        <p style="font-size:18px;">PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
        <span style="font-size:16px;">January 25, 2026 | OKADA BALLROOM 1–3</span></p>
        <button onclick="window.location.href='/?page=register'"
            style="background:#FFD400;color:black;font-size:22px;font-weight:800;">
            Register Here
        </button>
    </div>
    """, unsafe_allow_html=True)

# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)
    with st.form("form"):
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit", type="primary")

    if submit:
        if emp not in st.session_state.valid_employees:
            st.error("Employee ID NOT VERIFIED ❌")
        else:
            name = st.session_state.valid_employees[emp]
            st.session_state.entries.append({"emp": emp, "name": name})
            save_data()
            qr = generate_qr(f"{name}|{emp}")
            img = create_pass_image(name, emp, qr)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.success("Registered ✔️")
            st.image(buf.getvalue(), use_container_width=True)
            st.download_button("📥 Download Pass", buf.getvalue(), f"{emp}_pass.png")

    st.button("Back to Landing", on_click=go_to, args=("landing",), type="secondary")
    st.button("Admin Login", on_click=go_to, args=("admin",), type="secondary")

# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h1>Admin Panel</h1>", unsafe_allow_html=True)
    with st.form("admin_form"):
        uploaded = st.file_uploader("Upload Employee List", type=["xlsx"])
        st.text_input("Username", key="user")
        st.text_input("Password", type="password", key="pwd")
        submit = st.form_submit_button("Login", type="primary")
        if submit:
            if uploaded:
                df = pd.read_excel(uploaded)
                st.session_state.valid_employees = df.set_index("EMP ID")["Full Name"].to_dict()
                save_employees()
            login_admin()
    if st.session_state.get("login_error"):
        st.error("Invalid login")
        st.session_state.login_error = False
    st.button("Back to Landing", on_click=go_to, args=("landing",), type="secondary")

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)
    if st.session_state.entries:
        st.data_editor(pd.DataFrame(st.session_state.entries))
        st.button("🎰 Run Raffle", on_click=run_raffle, type="primary")
        if st.session_state.winner:
            st.markdown(f"<h1 style='color:gold'>{st.session_state.winner['name']}</h1>", unsafe_allow_html=True)
        st.button("Logout", on_click=logout, type="secondary")
        st.button("Delete All Entries", on_click=delete_all, type="secondary")
        st.button("Export CSV", on_click=export_csv, type="secondary")
    else:
        st.info("No registrations yet")
