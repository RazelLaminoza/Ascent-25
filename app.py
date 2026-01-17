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

    col1, col2, col3 = st.columns([5,1,5])
    with col2:
        st.button("Register", on_click=go_to, args=("register",))

# ---------------- REGISTER ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)

    with st.form("form"):
        emp = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")

    if submit:
        if not emp:
            st.error("Please enter Employee ID")
        elif any(e["emp"] == emp for e in st.session_state.entries):
            st.warning("Employee ID already registered")
        else:
            # Verify ID using saved list
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

    # NAVIGATION BUTTONS
    col1, col2 = st.columns(2)
    with col1:
        st.button("Back to Landing", on_click=go_to, args=("landing",))
    with col2:
        st.button("Admin Login", on_click=go_to, args=("admin",))

# ---------------- ADMIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h1>Admin Panel</h1>", unsafe_allow_html=True)

    # Upload Employee List here (ONLY in admin)
    uploaded_file = st.file_uploader("Upload Employee List (Excel)", type=["xlsx"])

    if uploaded_file:
        df_emp = pd.read_excel(uploaded_file)
        st.session_state.valid_employees = df_emp.set_index("EMP ID")["Full Name"].to_dict()
        save_employees()
        st.success("Employee list loaded and saved!")

    st.text_input("Username", key="user")
    st.text_input("Password", type="password", key="pwd")

    if st.button("Login", on_click=login_admin):
        pass

    if st.session_state.get("login_error", False):
        st.error("Invalid login")
        st.session_state.login_error = False

    st.button("Back to Landing", on_click=go_to, args=("landing",))

# ---------------- RAFFLE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        st.data_editor(df, key="raffle_editor")

        st.button("🎰 Run Raffle", on_click=run_raffle, key="run_raffle_btn")

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

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Logout", on_click=logout)
        with col2:
            st.button("Delete All Entries", on_click=delete_all)
        with col3:
            st.button("Export CSV", on_click=export_csv)

        if st.session_state.get("exported", False):
            st.success("CSV exported as entries.csv")

    else:
        st.info("No registrations yet")

    # <-- This is outside the if block so it always shows
    st.button("Back to Landing", on_click=go_to, args=("landing",))

