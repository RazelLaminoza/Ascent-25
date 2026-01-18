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
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
else:
    st.session_state.entries = []

# Load employee list (persisted)
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
    # Load background image
    bg = Image.open("bgna.png").convert("RGBA")
    bg = bg.resize((900, 500))

    img = Image.new("RGBA", (900, 500))
    img.paste(bg, (0, 0))

    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("Roboto-Regular.ttf", 42)
        font_small = ImageFont.truetype("Roboto-Regular.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    text_color = (255, 255, 255, 255)

    draw.text((40, 40), "ASCENT APAC 2026", fill=text_color, font=font_big)
    draw.text((40, 120), "FULL NAME:", fill=text_color, font=font_small)
    draw.text((40, 160), name, fill=text_color, font=font_big)

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

    html, body {{
        height: 100vh;
        overflow: hidden;
        margin: 0;
    }}

    #MainMenu, header, footer {{
        visibility: hidden;
        height: 0px;
    }}

    /* Minimal button style */
    button {{
        min-height: 48px;
        font-size: 18px;
        max-width: 280px;
        width: auto;
        margin: 8px auto;
        display: block;
        padding: 12px 24px;
        border-radius: 24px;
        border: none;
        cursor: pointer;
    }}

    /* Yellow primary */
    button[kind="primary"] {{
        background-color: #FFD400 !important;
        color: black !important;
        font-weight: 700;
    }}

    /* Black secondary */
    button[kind="secondary"] {{
        background-color: #000000 !important;
        color: white !important;
        font-weight: 500;
    }}

    /* Minimal form inputs */
    .stTextInput > div > input {{
        max-width: 320px;
        margin: 0 auto;
    }}

    .stForm {{
        max-width: 360px;
        margin: 0 auto;
    }}

    h1, p {{
        color: white;
        text-align: center;
        text-shadow: 1px 1px 4px rgba(0,0,0,.7);
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("bgna.png")

# ---------------- NAVIGATION ----------------
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
    df = pd.DataFrame(st.session_state.entries)
    df.to_csv("entries.csv", index=False)
    st.session_state.exported = True

# ---------------- LANDING PAGE ----------------
# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown(
        f"""
        <div style='height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <img src='data:image/png;base64,{base64.b64encode(open("2.png","rb").read()).decode()}' width='160'/>
            <img src='data:image/png;base64,{base64.b64encode(open("1.png","rb").read()).decode()}' style='width:70%; max-width:900px;'/>
            <p>
                PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
                <span style="font-size:16px;">January 25, 2026 | OKADA BALLROOM 1–3</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # CENTER BUTTON using columns
    col1, col2, col3 = st.columns([7, 2, 7])

    with col2:
        st.button("Register", on_click=go_to, args=("register",), type="primary")


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

                img_b64 = base64.b64encode(pass_bytes).decode()

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        justify-content:center;
                        margin-top: 20px;
                    ">
                        <div style="
                            background: rgba(255, 255, 255, 0.12);
                            border: 1px solid rgba(255, 255, 255, 0.25);
                            border-radius: 18px;
                            padding: 16px;
                            backdrop-filter: blur(8px);
                            -webkit-backdrop-filter: blur(8px);
                            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
                            max-width: 520px;
                            width: 100%;
                        ">
                            <img src="data:image/png;base64,{img_b64}" style="width:100%; border-radius: 12px;" />
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.download_button(
                    "📥 Download Pass (PNG)",
                    pass_bytes,
                    file_name=f"{emp}_event_pass.png",
                    mime="image/png",
                    type="primary"
                )

    st.button("Back to Landing", on_click=go_to, args=("landing",), type="secondary")
    st.button("Admin Login", on_click=go_to, args=("admin",), type="secondary")

# ---------------- ADMIN ----------------
# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h1>Admin Panel</h1>", unsafe_allow_html=True)

    # Create 3 columns and use middle column for content
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div style='max-width: 280px; margin: 0 auto;'>", unsafe_allow_html=True)

        st.text_input("Username", key="user")
        st.text_input("Password", type="password", key="pwd")

        st.button("Login", on_click=login_admin, type="primary")

        if st.session_state.get("login_error", False):
            st.error("Invalid login")
            st.session_state.login_error = False

        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.2)'/>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center;'>Upload Employee List (Excel)</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["xlsx"])

        if uploaded_file:
            df_emp = pd.read_excel(uploaded_file)
            st.session_state.valid_employees = df_emp.set_index("EMP ID")["Full Name"].to_dict()
            save_employees()
            st.success("Employee list loaded and saved!")

        st.button("Back to Landing", on_click=go_to, args=("landing",), type="secondary")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display:flex; justify-content:center;">
            <div style="width:100%; max-width:520px;">
        """,
        unsafe_allow_html=True
    )

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        st.data_editor(df, key="raffle_editor")

        st.button("🎰 Run Raffle", on_click=run_raffle, key="run_raffle_btn", type="primary")

        if st.session_state.winner is not None:
            st.markdown(
                f"""
                <div style="text-align:center;margin-top:40px;">
                    <h2 style="color:white;">🎉 WINNER 🎉</h2>
                    <h1 style="color:gold;font-size:80px;">
                        {st.session_state.winner['name']}
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.button("Logout", on_click=logout, type="secondary")
        st.button("Delete All Entries", on_click=delete_all, type="secondary")
        st.button("Export CSV", on_click=export_csv, type="secondary")

        if st.session_state.get("exported", False):
            st.success("CSV exported as entries.csv")
    else:
        st.info("No registrations yet")

    st.button("Back to Landing", on_click=go_to, args=("landing",), type="secondary")

    st.markdown("</div></div>", unsafe_allow_html=True)
