import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
import json
import time
import os
from PIL import Image, ImageDraw, ImageFont

def add_custom_font():
    font_path = "PPNeueMachina-PlainUltrabold.ttf"
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            font_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
                @font-face {{
                    font-family: "PPNeueMachina";
                    src: url("data:font/ttf;base64,{font_b64}") format("truetype");
                }}
                * {{ font-family: "PPNeueMachina" !important; }}
                [class*="css"] {{ font-family: "PPNeueMachina" !important; }}
                button, input, textarea, select {{ font-family: "PPNeueMachina" !important; }}
            </style>
        """, unsafe_allow_html=True)

add_custom_font()

st.set_page_config(
    page_title="ASCENT APAC 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STORAGE ----------------
DATA_FILE = "raffle_data.json"
EMPLOYEE_FILE = "employees.json"
FILE_PATH = "entries.csv"

# ---------------- SESSION STATE (ONE TIME ONLY) ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "admin" not in st.session_state:
    st.session_state.admin = False

if "winner" not in st.session_state:
    st.session_state.winner = None

if "entries" not in st.session_state:
    st.session_state.entries = []

if "valid_employees" not in st.session_state:
    st.session_state.valid_employees = {}

if "go_admin" not in st.session_state:
    st.session_state.go_admin = False

# Load saved entries
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])

# Load employees list
if os.path.exists(EMPLOYEE_FILE):
    with open(EMPLOYEE_FILE, "r") as f:
        st.session_state.valid_employees = json.load(f)

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

def resize_keep_aspect(img, max_size):
    img = img.convert("RGBA")
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def create_pass_image(name, emp, qr_img):
    bg = Image.open("bgna.png").convert("RGBA")
    bg = bg.resize((900, 500))
    img = Image.new("RGBA", (900, 500))
    img.paste(bg, (0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("CourierPrime-Bold.ttf", 42)
        font_small = ImageFont.truetype("CourierPrime-Bold.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    text_color = (255, 255, 255, 255)
    logo1 = Image.open("1.png").convert("RGBA")
    logo2 = Image.open("2.png").convert("RGBA")
    logo1 = resize_keep_aspect(logo1, (120, 120))
    logo2 = resize_keep_aspect(logo2, (120, 120))
    img.paste(logo1, (620, 30), logo1)
    img.paste(logo2, (760, 30), logo2)

    draw.text((40, 40), "ASCENT APAC 2026", fill=text_color, font=font_big)
    draw.text((40, 120), "FULL NAME:", fill=text_color, font=font_big)
    draw.text((40, 160), name, fill=text_color, font=font_small)
    draw.text((40, 260), "EMPLOYEE NO:", fill=text_color, font=font_small)
    draw.text((40, 300), emp, fill=text_color, font=font_big)
    draw.text((40, 380),
              "Present this pre-registration pass\nat the check-in counter",
              fill=text_color, font=font_small)

    qr_img = qr_img.resize((220, 220))
    img.paste(qr_img, (620, 140), qr_img.convert("RGBA"))
    return img.convert("RGB")

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
        overflow: hidden;
    }}
    html, body {{ height: 100vh; overflow: hidden; margin: 0; }}
    #MainMenu, header, footer {{ visibility: hidden; height: 0px; }}
    button {{ min-height: 48px; font-size: 18px; max-width: 280px; width: auto; margin: 8px auto; display: block; padding: 12px 24px; border-radius: 24px; border: none; cursor: pointer; }}
    button[kind="primary"] {{ background-color: #FFD400 !important; color: black !important; font-weight: 700; }}
    button[kind="secondary"] {{ background-color: #000000 !important; color: white !important; font-weight: 500; }}
    .stTextInput > div > input {{ max-width: 320px; margin: 0 auto; }}
    .stForm {{ max-width: 360px; margin: 0 auto; }}
    h1, p {{ color: white; text-align: center; text-shadow: 1px 1px 4px rgba(0,0,0,.7); }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

def go_to(page_name):
    st.session_state.page = page_name

def login_admin():
    user = st.session_state["user"]
    pwd = st.session_state["pwd"]
    if user == st.secrets["ADMIN_USER"] and pwd == st.secrets["ADMIN_PASS"]:
        st.session_state.admin = True
        st.session_state.page = "raffle"
    else:
        st.session_state.login_error = True

def run_raffle():
    if not st.session_state.entries:
        return
    st.session_state.winner = None
    placeholder = st.empty()
    start_time = time.time()
    while time.time() - start_time < 10:
        current = random.choice(st.session_state.entries)
        placeholder.markdown(
            f"<div style='text-align:center;margin-top:30px;'><h2 style='color:white;'>Shuffling...</h2><h1 style='color:gold;font-size:60px;'>{current['Full Name']}</h1></div>",
            unsafe_allow_html=True)
        time.sleep(0.05)
    st.session_state.winner = random.choice(st.session_state.entries)
    placeholder.empty()

def logout():
    st.session_state.admin = False
    st.session_state.page = "landing"
    st.session_state.winner = None

def delete_all_entries():
    st.session_state.entries = []
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    st.success("All entries deleted.")

def export_csv():
    df = pd.DataFrame(st.session_state.entries)
    df.to_csv("entries.csv", index=False)
    st.session_state.exported = True

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown("""<style> ... </style>""", unsafe_allow_html=True)
    st.button("Pre-register", on_click=go_to, args=("register",), type="primary")

# ---------------- REGISTER PAGE ----------------
if st.session_state.page == "register":
    st.markdown("<h1 style='color:white;'>Register Here</h1>", unsafe_allow_html=True)

    with st.form("form"):
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit", type="primary")

        if submit:
            if emp == "admin123":
                st.session_state.go_admin = True
            elif not emp:
                st.error("Employee ID NOT VERIFIED ❌")
            elif any(e["emp"] == emp for e in st.session_state.entries):
                st.error("You already registered ❌")
            elif emp not in st.session_state.valid_employees:
                st.error("Employee ID NOT VERIFIED ❌")
            else:
                name = st.session_state.valid_employees.get(emp, "Unknown")
                st.session_state.entries.append({"emp": emp, "Full Name": name})
                save_data()

                qr_img = generate_qr(f"{name} | {emp}")
                pass_img = create_pass_image(name, emp, qr_img)

                buf = io.BytesIO()
                pass_img.save(buf, format="PNG")
                pass_bytes = buf.getvalue()

                st.session_state.pass_bytes = pass_bytes
                st.session_state.pass_emp = emp

                st.success("Registered and VERIFIED ✔️")

    if st.session_state.get("pass_bytes"):
        st.download_button(
            "📥 Download Pass (PNG)",
            st.session_state.pass_bytes,
            file_name=f"{st.session_state.pass_emp}_event_pass.png",
            mime="image/png",
            type="primary"
        )

    if st.session_state.get("go_admin", False):
        st.session_state.go_admin = False
        go_to("admin")

# ---------------- ADMIN PAGE ----------------
if st.session_state.page == "admin":
    st.markdown("<h1>🔐 Admin Panel</h1>", unsafe_allow_html=True)

    with st.form("admin_form"):
        uploaded_file = st.file_uploader("Upload Employee List (Excel)", type=["xlsx"])
        st.text_input("Username", key="user")
        st.text_input("Password", type="password", key="pwd")
        submit = st.form_submit_button("Login", type="primary")

        if submit:
            if uploaded_file:
                df = pd.read_excel(uploaded_file)
                st.session_state.valid_employees = dict(zip(df["EmployeeID"].astype(str), df["Full Name"]))
                save_employees()

            if login_admin():
                st.success("Login successful")
            else:
                st.error("Invalid login")

    if not st.session_state.admin:
        st.button("Back to Landing", on_click=go_to, args=("landing",), key="back_to_landing_admin")

    if st.session_state.admin:
        df = pd.DataFrame(st.session_state.entries)
        st.dataframe(df)
        st.button("🗑️ Delete All Entries", on_click=delete_all_entries, type="secondary")
        st.button("🎰 Enter Raffle", on_click=go_to, args=("raffle",), type="primary")
        st.button("Logout", on_click=logout)

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.session_state.page = "admin"

    st.markdown("<h1>🎰 Raffle Draw</h1>", unsafe_allow_html=True)
    st.button("🎰 Run Raffle", on_click=run_raffle, type="primary")

    if st.session_state.winner:
        st.markdown(
            f"<div style='text-align:center;margin-top:40px;'><h2>🎉 WINNER 🎉</h2><h1 style='color:gold;font-size:70px;'>{st.session_state.winner['Full Name']}</h1></div>",
            unsafe_allow_html=True
        )

    st.button("Logout", on_click=logout)
