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

# Load raffle entries
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        st.session_state.entries = json.load(f).get("entries", [])
else:
    st.session_state.entries = []

# Load employee list
if os.path.exists(EMPLOYEE_FILE):
    with open(EMPLOYEE_FILE, "r") as f:
        st.session_state.valid_employees = json.load(f)
else:
    st.session_state.valid_employees = {}

# Session defaults
st.session_state.setdefault("page", "landing")
st.session_state.setdefault("admin", False)
st.session_state.setdefault("winner", None)

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
    img = Image.new("RGB", (900, 500), "#ff4b5c")
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 42)
        font_small = ImageFont.truetype("arial.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    draw.text((40, 40), "ASCENT APAC 2026", fill="white", font=font_big)
    draw.text((40, 120), "FULL NAME:", fill="white", font=font_small)
    draw.text((40, 160), name, fill="white", font=font_big)

    draw.text((40, 260), "EMPLOYEE NO:", fill="white", font=font_small)
    draw.text((40, 300), emp, fill="white", font=font_big)

    draw.text(
        (40, 380),
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
    }}

    html, body {{
        height: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        margin: 0;
    }}

    #MainMenu, header, footer {{
        visibility: hidden;
        height: 0px;
    }}

    h1, p {{
        color: white;
        text-align: center;
        text-shadow: 1px 1px 4px rgba(0,0,0,.7);
    }}

    /* BUTTON STYLE */
    button {{
        min-height: 48px;
        font-size: 18px;
        max-width: 260px;   /* minimal size */
        width: auto;        /* not full width */
        margin: 8px auto;
        padding: 12px 24px;
        display: block;
        border-radius: 24px;
        border: none;
        cursor: pointer;
    }}

    button[kind="primary"] {{
        background-color: #FFD400 !important;
        color: black !important;
        font-weight: 700;
    }}

    button[kind="secondary"] {{
        background-color: #000000 !important;
        color: white !important;
        font-weight: 500;
    }}

    /* INPUT STYLE (optional, but looks like login UI) */
    .stTextInput > div > input {{
        max-width: 320px;
        margin: 0 auto;
    }}

    .stForm {{
        max-width: 360px;
        margin: 0 auto;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

# ---------------- NAVIGATION ----------------
def go_to(page):
    st.session_state.page = page

def login_admin():
    if (
        st.session_state.get("user") == st.secrets["ADMIN_USER"]
        and st.session_state.get("pwd") == st.secrets["ADMIN_PASS"]
    ):
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
    st.markdown(
        f"""
        <div style="min-height:100vh; display:flex; flex-direction:column;
        justify-content:center; align-items:center; padding:20px;">
            <img src="data:image/png;base64,{base64.b64encode(open("2.png","rb").read()).decode()}" width="140"/>
            <img src="data:image/png;base64,{base64.b64encode(open("1.png","rb").read()).decode()}"
                 style="width:100%; max-width:900px;"/>
            <p>
                PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
                <span style="font-size:16px;">January 25, 2026 | OKADA BALLROOM 1–3</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # CENTERED REGISTER BUTTON
    st.markdown(
        "<div style='display:flex; justify-content:center;'>"
        "<div style='width:100%; max-width:360px;'>",
        unsafe_allow_html=True
    )

    st.button("Register", on_click=go_to, args=("register",), type="primary")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)

    with st.form("form"):
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit", type="primary")

    if submit:
        if not emp:
            st.error("Please enter Employee ID")
        elif any(e["emp"] == emp for e in st.session_state.entries):
            st.warning("Employee ID already registered")
        elif emp not in st.session_state.valid_employees:
            st.error("Employee ID NOT VERIFIED ❌")
        else:
            name = st.session_state.valid_employees[emp]
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
                mime="image/png",
                type="primary"
            )

    st.button("⬅ Back to Landing", on_click=go_to, args=("landing",), type="secondary")
    st.button("🔐 Admin Login", on_click=go_to, args=("admin",), type="secondary")

# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h1>Admin Panel</h1>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload Employee List (Excel)", type=["xlsx"])
    if uploaded:
        df = pd.read_excel(uploaded)
        st.session_state.valid_employees = df.set_index("EMP ID")["Full Name"].to_dict()
        save_employees()
        st.success("Employee list saved")

    st.text_input("Username", key="user")
    st.text_input("Password", type="password", key="pwd")

    st.button("Login", on_click=login_admin, type="primary")

    if st.session_state.get("login_error"):
        st.error("Invalid login")
        st.session_state.login_error = False

    st.button("⬅ Back to Landing", on_click=go_to, args=("landing",), type="secondary")

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    if st.session_state.entries:
        st.dataframe(pd.DataFrame(st.session_state.entries), use_container_width=True)

        st.button("🎰 Run Raffle", on_click=run_raffle, type="primary")

        if st.session_state.winner:
            st.markdown(
                f"<h1 style='color:gold;text-align:center;'>🎉 {st.session_state.winner['name']} 🎉</h1>",
                unsafe_allow_html=True
            )

        st.button("🗑 Delete All", on_click=delete_all, type="secondary")
        st.button("📤 Export CSV", on_click=export_csv, type="secondary")
        st.button("🚪 Logout", on_click=logout, type="secondary")
    else:
        st.info("No registrations yet")

    st.button("⬅ Back to Landing", on_click=go_to, args=("landing",), type="secondary")
