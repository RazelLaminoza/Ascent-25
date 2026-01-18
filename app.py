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

# ---------------- CSS ----------------
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
    }}
    html, body {{
        background: transparent;
    }}
    #MainMenu, header, footer {{
        visibility: hidden;
    }}

    .card {{
        background: rgba(0,0,0,0.45);
        padding: 22px;
        border-radius: 18px;
        width: 100%;
        max-width: 420px;
        margin: auto;
    }}

    .stButton>button {{
        background-color: #FFD700 !important;
        color: black !important;
        border-radius: 12px !important;
        height: 44px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }}

    .stButton>button.secondary {{
        background-color: black !important;
        color: white !important;
    }}

    .stTextInput>div>div>input {{
        border-radius: 12px !important;
        padding: 12px !important;
        background: rgba(255,255,255,0.85) !important;
    }}

    h1, p {{
        color: white;
        text-align: center;
        margin: 0;
    }}

    .center {{
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }}

    .btn-row {{
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

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

    color = (255,255,255,255)
    draw.text((40, 40), "ASCENT APAC 2026", fill=color, font=font_big)
    draw.text((40, 120), "NAME:", fill=color, font=font_small)
    draw.text((40, 160), name, fill=color, font=font_big)
    draw.text((40, 260), "EMP:", fill=color, font=font_small)
    draw.text((40, 300), emp, fill=color, font=font_big)

    qr_img = qr_img.resize((220, 220))
    img.paste(qr_img, (620, 140), qr_img.convert("RGBA"))
    return img.convert("RGB")

def go_to(page):
    st.session_state.page = page

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
    st.markdown("<div class='card center'>", unsafe_allow_html=True)

    st.image("2.png", width=120)
    st.image("1.png", width=350)

    st.markdown("<p>PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px;'>January 25, 2026 | OKADA BALLROOM 1–3</p>", unsafe_allow_html=True)

    st.button("Register", on_click=go_to, args=("register",))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<div class='card center'>", unsafe_allow_html=True)
    st.markdown("<h1>Register</h1>", unsafe_allow_html=True)

    with st.form("form"):
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")

    if submit:
        if not emp:
            st.error("Please enter Employee ID")
        elif any(e["emp"] == emp for e in st.session_state.entries):
            st.warning("Employee ID already registered")
        else:
            if emp not in st.session_state.valid_employees:
                st.error("Employee ID NOT VERIFIED ❌")
            else:
                name = st.session_state.valid_employees.get(emp, "Unknown")
                st.session_state.entries.append({"emp": emp, "name": name})
                save_data()

                qr_img = generate_qr(f"{name} | {emp}")
                pass_img = create_pass_image(name, emp, qr_img)

                buf = io.BytesIO()
                pass_img.save(buf, format="PNG")
                pass_bytes = buf.getvalue()

                st.success("Registered and VERIFIED ✔️")
                st.image(pass_bytes, use_container_width=True)

                st.download_button(
                    "📥 Download Pass (PNG)",
                    pass_bytes,
                    file_name=f"{emp}_event_pass.png",
                    mime="image/png"
                )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="btn-row">
        <button onclick="window.location.href='?page=landing'" class="secondary" style="padding:10px 24px; border-radius:12px;">Back</button>
        <button onclick="window.location.href='?page=admin'" class="secondary" style="padding:10px 24px; border-radius:12px;">Admin</button>
    </div>
    """, unsafe_allow_html=True)

# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<div class='card center'>", unsafe_allow_html=True)
    st.markdown("<h1>Admin Panel</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Employee List (Excel)", type=["xlsx"])

    if uploaded_file:
        df_emp = pd.read_excel(uploaded_file)
        st.session_state.valid_employees = df_emp.set_index("EMP ID")["Full Name"].to_dict()
        save_employees()
        st.success("Employee list loaded and saved!")

    st.text_input("Username", key="user")
    st.text_input("Password", type="password", key="pwd")

    st.button("Login", on_click=login_admin)

    if st.session_state.get("login_error", False):
        st.error("Invalid login")
        st.session_state.login_error = False

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="btn-row">
        <button onclick="window.location.href='?page=landing'" class="secondary" style="padding:10px 24px; border-radius:12px;">Back</button>
    </div>
    """, unsafe_allow_html=True)

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<div class='card center'>", unsafe_allow_html=True)
    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        st.data_editor(df, key="raffle_editor")

        st.button("🎰 Run Raffle", on_click=run_raffle)

        if st.session_state.winner is not None:
            st.markdown(
                f"<h2 style='color:gold;'>🎉 WINNER: {st.session_state.winner['name']}</h2>",
                unsafe_allow_html=True
            )

        st.markdown("""
        <div class="btn-row">
            <button onclick="window.location.href='?page=landing'" class="secondary" style="padding:10px 24px; border-radius:12px;">Logout</button>
            <button onclick="window.location.href='?page=landing'" class="secondary" style="padding:10px 24px; border-radius:12px;">Delete All</button>
            <button onclick="window.location.href='?page=landing'" class="secondary" style="padding:10px 24px; border-radius:12px;">Export CSV</button>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("exported", False):
            st.success("CSV exported as entries.csv")

    else:
        st.info("No registrations yet")

    st.markdown("</div>", unsafe_allow_html=True)
