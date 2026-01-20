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

                /* Apply font everywhere in Streamlit */
                * {{
                    font-family: "PPNeueMachina" !important;
                }}

                /* Extra strong override for Streamlit internal elements */
                [class*="css"] {{
                    font-family: "PPNeueMachina" !important;
                }}

                /* Buttons and Inputs */
                button, input, textarea, select {{
                    font-family: "PPNeueMachina" !important;
                }}
            </style>
        """, unsafe_allow_html=True)

add_custom_font()




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

# ---- ADD THIS FUNCTION HERE ----
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.getsize(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines
# -------------------------------

def resize_keep_aspect(img, max_size):
    img = img.convert("RGBA")
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def create_pass_image(name, emp, qr_img):
    # Load background image
    bg = Image.open("bgna.png").convert("RGBA")
    bg = bg.resize((900, 500))

    img = Image.new("RGBA", (900, 500))
    img.paste(bg, (0, 0))

    draw = ImageDraw.Draw(img)

    # Load fonts (regular)
    try:
        font_big = ImageFont.truetype("CourierPrime-Bold.ttf", 42)
        font_small = ImageFont.truetype("CourierPrime-Bold.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    text_color = (255, 255, 255, 255)

    # Add 1.png and 2.png at the top-right (no stretching)
    logo1 = Image.open("1.png").convert("RGBA")
    logo2 = Image.open("2.png").convert("RGBA")

    logo1 = resize_keep_aspect(logo1, (120, 120))
    logo2 = resize_keep_aspect(logo2, (120, 120))

    img.paste(logo1, (620, 30), logo1)
    img.paste(logo2, (760, 30), logo2)

    # Text
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
    if not st.session_state.entries:
        return

    st.session_state.winner = None
    placeholder = st.empty()

    start_time = time.time()
    while time.time() - start_time < 10:
        current = random.choice(st.session_state.entries)

        placeholder.markdown(
            f"""
            <div style="text-align:center; margin-top:30px;">
                <h2 style="color:white;">Shuffling...</h2>
                <h1 style="color:gold; font-size:60px;">
                    {current['Full Name']}
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.05)

    st.session_state.winner = random.choice(st.session_state.entries)
    placeholder.empty()


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
if st.session_state.page == "landing":

    st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    html, body { overflow: hidden !important; height: 100% !important; }

    .landing {
        position: relative;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin-top: -90px;
    }

    /* Style the Streamlit button */
    div[data-testid="stButton"] > button {
        width: 360px !important;
        height: 55px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        background-color: #FFD700 !important;
        color: black !important;
        border: none !important;
        border-radius: 8px !important;
    }

    /* Position by X and Y */
    #landing-button {
        position: absolute;
        left: 10%;   /* X axis */
        top: 20%;    /* Y axis */
        transform: translate(-50%, -50%);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="landing">
            <img src='data:image/png;base64,{base64.b64encode(open("2.png","rb").read()).decode()}' width='160'/>
            <img src='data:image/png;base64,{base64.b64encode(open("1.png","rb").read()).decode()}' style='width:70%; max-width:900px; margin-top:20px;'/>
            <p style="font-size:18px; line-height:1.3;">
                PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
                <span style="font-size:16px;">January 25, 2026 | OKADA BALLROOM 1–3</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Streamlit button with id for positioning
    st.button(
        "Pre-register",
        on_click=go_to,
        args=("register",),
        type="primary",
        key="landing_register_1"
    )



# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)

    # ---------- BUTTON STYLE ----------
    st.markdown(
        """
        <style>
        /* Submit button */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            max-width: 520px !important;
            height: 55px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            background-color: #FFD700 !important;
            color: black !important;
            border: none !important;
            border-radius: 8px !important;
            margin: 0 auto !important;
            padding: 0 !important;
        }

        div[data-testid="stFormSubmitButton"] > button span,
        div[data-testid="stFormSubmitButton"] > button span * {
            color: black !important;
        }

        /* Back + Admin buttons */
        div[data-testid="stButton"] > button {
            width: 100% !important;
            max-width: 520px !important;
            height: 55px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ------------------ FORM ------------------
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
                        <div style="display:flex; justify-content:center; margin-top: 20px;">
                            <div style="
                                background: #FFD700;
                                color: #000000;
                                border: 1px solid rgba(0, 0, 0, 0.25);
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

    # ------------------ DOWNLOAD BUTTON OUTSIDE FORM ------------------
    if "pass_bytes" in locals():
        st.download_button(
            "📥 Download Pass (PNG)",
            pass_bytes,
            file_name=f"{emp}_event_pass.png",
            mime="image/png",
            type="primary"
        )

    # ------------------ BACK + ADMIN BUTTONS ------------------
    col1, col2 = st.columns(2)
    with col1:
        st.button("Back to Landing", on_click=go_to, args=("landing",), type="secondary")

    with col2:
        st.button("Admin Login", on_click=go_to, args=("admin",), type="secondary")

#-----------------admin----------------
# ---------------- FILE STORAGE ----------------
FILE_PATH = "entries.csv"

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "admin"

if "admin" not in st.session_state:
    st.session_state.admin = False

if "entries" not in st.session_state:
    st.session_state.entries = []

if "winner" not in st.session_state:
    st.session_state.winner = None

# ---------------- CREDENTIALS ----------------
USERNAME = "admin"
PASSWORD = "admin123"


# ---------------- FUNCTIONS ----------------
def load_entries():
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        st.session_state.entries = df.to_dict("records")


def save_entries():
    df = pd.DataFrame(st.session_state.entries)
    df.to_csv(FILE_PATH, index=False)


def go_to(page):
    st.session_state.page = page


def login_admin():
    if st.session_state.user == USERNAME and st.session_state.pwd == PASSWORD:
        st.session_state.admin = True
        return True
    return False


def logout():
    st.session_state.admin = False
    st.session_state.winner = None
    st.session_state.page = "admin"


def run_raffle():
    if st.session_state.entries:
        st.session_state.winner = random.choice(st.session_state.entries)


def shuffle_effect():
    if not st.session_state.entries:
        return

    placeholder = st.empty()

    # Shuffle effect
    for _ in range(15):
        temp = random.choice(st.session_state.entries)
        placeholder.markdown(
            f"""
            <div style="text-align:center;margin-top:40px;">
                <h2>🎉 SHUFFLING 🎉</h2>
                <h1 style="color:gold;font-size:70px;">
                    {temp["Full Name"]}
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.08)

    # Final winner
    st.session_state.winner = random.choice(st.session_state.entries)
    placeholder.empty()


# ---------------- LOAD ENTRIES ON START ----------------
load_entries()


# ---------------- ADMIN PAGE ----------------
if st.session_state.page == "admin":

    st.markdown("<h1>🔐 Admin Panel</h1>", unsafe_allow_html=True)
    st.button("Back to Landing", on_click=go_to, args=("landing",), key="back_to_landing_admin")

    with st.form("admin_form"):
        uploaded_file = st.file_uploader(
            "Upload Employee List (Excel)",
            type=["xlsx"]
        )

        st.text_input("Username", key="user")
        st.text_input("Password", type="password", key="pwd")

        submit = st.form_submit_button("Login", type="primary")

        if submit:
            if uploaded_file:
                df = pd.read_excel(uploaded_file)

                df = df.rename(columns={
                    "employee id": "Employee ID",
                    "Emp ID": "Employee ID",
                    "emp_id": "Employee ID",
                    "Full name": "Full Name",
                    "Name": "Full Name"
                })

                if "Employee ID" not in df.columns or "Full Name" not in df.columns:
                    st.error("Excel must contain 'Employee ID' and 'Full Name'")
                else:
                    df = df.drop_duplicates("Employee ID")
                    st.session_state.entries = df[["Employee ID", "Full Name"]].to_dict("records")
                    save_entries()

            if login_admin():
                st.success("Login successful")
            else:
                st.error("Invalid login")


        

    # ---- SHOW TABLE (ADMIN ONLY) ----
    if st.session_state.admin and st.session_state.entries:

        st.markdown("### Employee List")
        df = pd.DataFrame(st.session_state.entries)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Download CSV",
            csv,
            "entries.csv",
            "text/csv",
            key="download_csv"
        )

        st.button(
            "🎰 Enter Raffle",
            on_click=go_to,
            args=("raffle",),
            type="primary",
            key="enter_raffle"
        )

    if st.session_state.admin:
        st.markdown("---")
        st.button("Logout", on_click=logout, key="logout_admin")
        st.button("Back to Landing", on_click=go_to, args=("landing",), key="back_to_landing_admin")

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":

    if not st.session_state.admin:
        st.session_state.page = "admin"

    st.markdown("<h1>🎰 Raffle Draw</h1>", unsafe_allow_html=True)

    st.button("🎰 Run Raffle", on_click=shuffle_effect, type="primary", key="run_raffle")

    if st.session_state.winner:
        winner_name = (
            st.session_state.winner.get("Full Name")
            if isinstance(st.session_state.winner, dict)
            else st.session_state.winner
        )

        st.markdown(
            f"""
            <div style="text-align:center;margin-top:40px;">
                <h2>🎉 WINNER 🎉</h2>
                <h1 style="color:gold;font-size:70px;">
                    {winner_name}
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.button("Logout", on_click=logout, key="logout_raffle")
