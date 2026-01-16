import streamlit as st
import random
import qrcode
import io
import pandas as pd
import base64
import time
import json
import os

# ---------------- STORAGE FILE ----------------
DATA_FILE = "raffle_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
        st.session_state.winner = data.get("winner", None)
else:
    st.session_state.entries = []
    st.session_state.winner = None

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin" not in st.session_state:
    st.session_state.admin = False

# ---------------- FUNCTIONS ----------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "entries": st.session_state.entries,
            "winner": st.session_state.winner
        }, f)

def generate_qr(data):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <!-- Load Roboto font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Roboto', sans-serif;
    }}
    h1, h2, h3 {{
        color: white;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        font-family: 'Roboto', sans-serif;
    }}

    /* Transparent, modern form */
    .stForm {{
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 20px 25px !important;
        border-radius: 15px !important;
        backdrop-filter: blur(8px);
        font-family: 'Roboto', sans-serif !important;
        box-shadow: none !important;
        border: none !important;
    }}

    .stTextInput>div>div>input, .stTextInput>div>div>textarea {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        color: white !important;
        font-family: 'Roboto', sans-serif !important;
    }}

    .stTextInput>div>div>input::placeholder {{
        color: rgba(255,255,255,0.6) !important;
    }}

    button[kind="primary"] {{
        background-color: #FFD000 !important;
        color: black !important;
        border-radius: 30px !important;
        height: 55px;
        font-size: 18px;
        font-weight: 700;
        border: none;
        font-family: 'Roboto', sans-serif !important;
    }}
    button[kind="primary"]:hover {{
        background-color: #FFB700 !important;
    }}

    .fixed-logo {{
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
    }}

    [data-testid="stAppViewContainer"] {{
        padding: 0 !important;
        margin: 0 !important;
    }}
    [data-testid="block-container"] {{
        padding: 0.5rem !important;
        max-width: 100% !important;
    }}
    html, body {{
        overflow: hidden !important;
    }}
    ::-webkit-scrollbar {{
        width: 0px;
        height: 0px;
        display: none;
    }}
    * {{
        scrollbar-width: none;
    }}
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    @media (max-width: 768px) {{
        html, body {{ overflow-y: auto !important; }}
        .fixed-logo {{ position: static; margin-bottom: 16px; }}
        h1 {{ font-size: 32px !important; }}
        img {{ max-width: 100% !important; height: auto !important; }}
        button {{ width: 100% !important; font-size: 16px !important; height: 50px !important; }}
        .stForm {{ max-width: 90% !important; padding: 18px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg_local("bgna.png")

# Friendly URL
FRIENDLY_URL_HTML = '<a href="https://ascent-25-mjulgiqllfljvmfdphzn5c.streamlit.app/" target="_blank">https://ascentapac2026.com/</a>'

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown('<div class="fixed-logo">', unsafe_allow_html=True)
    st.image("2.png", width=160)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.image("1.png", use_column_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    colb1, colb2, colb3 = st.columns([2,1,2])
    with colb2:
        if st.button("Register", use_container_width=True):
            st.session_state.page = "register"

    st.markdown(
        f'<p style="text-align:center;color:white;font-size:18px">Visit our app: {FRIENDLY_URL_HTML}</p>',
        unsafe_allow_html=True
    )

# ---------------- REGISTRATION PAGE ----------------
elif st.session_state.page == "register":
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)
    with st.form("register_form"):
        name = st.text_input("Full Name")
        emp_number = st.text_input("Employee ID")
        submit = st.form_submit_button("Submit")
        if submit:
            if name and emp_number:
                if any(e["emp_number"] == emp_number for e in st.session_state.entries):
                    st.warning("Employee ID already registered")
                else:
                    st.session_state.entries.append({"name": name, "emp_number": emp_number})
                    save_data()
                    st.success("Registration successful!")
                    qr = generate_qr(f"Name: {name}\nEmployee ID: {emp_number}")
                    buf = io.BytesIO()
                    qr.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="Your QR Code")
            else:
                st.error("Please fill both Name and Employee ID")
    if not st.session_state.admin:
        if st.button("Admin Login"):
            st.session_state.page = "admin"

    st.markdown(
        f'<p style="text-align:center;color:white;font-size:16px">App link: {FRIENDLY_URL_HTML}</p>',
        unsafe_allow_html=True
    )

# ---------------- ADMIN LOGIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h2>Admin Login</h2>", unsafe_allow_html=True)
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅ Back"):
            st.session_state.page = "register"
    with col2:
        if st.button("Login"):
            if user == st.secrets["ADMIN_USER"] and pwd == st.secrets["ADMIN_PASS"]:
                st.session_state.admin = True
                st.session_state.page = "raffle"
            else:
                st.error("Invalid credentials")

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":
    if not st.session_state.admin:
        st.warning("You must be an admin to access this page")
        if st.button("⬅ Back to Register"):
            st.session_state.page = "register"
        st.stop()

    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅ Register"):
            st.session_state.page = "register"
    with nav2:
        if st.button("🚪 Logout Admin"):
            st.session_state.admin = False
            st.session_state.page = "landing"

    entries = st.session_state.entries
    if entries:
        st.subheader("Registered Employees (Editable)")
        df = pd.DataFrame(entries)
        edited_df = st.data_editor(df, num_rows="dynamic")
        if st.button("Save Table Changes"):
            st.session_state.entries = edited_df.to_dict("records")
            save_data()
            st.success("Table changes saved!")

        excel = io.BytesIO()
        edited_df.to_excel(excel, index=False)
        excel.seek(0)
        st.download_button("Download Excel", excel, "registered_employees.xlsx")

        placeholder = st.empty()

        if st.button("Run Raffle"):
            # Flashing names
            for _ in range(30):
                current = random.choice(st.session_state.entries)
                placeholder.markdown(
                    f"<h1 style='color:white;font-size:70px'>{current['name']} ({current['emp_number']})</h1>",
                    unsafe_allow_html=True
                )
                time.sleep(0.07)

            # Pick winner
            winner = random.choice(st.session_state.entries)
            st.session_state.winner = winner
            save_data()

            # Show winner
            placeholder.markdown(
                f"<h1 style='color:#FFD700;text-shadow:2px 2px 4px rgba(0,0,0,0.7); font-size:80px'>{winner['name']} ({winner['emp_number']})</h1>",
                unsafe_allow_html=True
            )

            # Full-screen confetti
            st.components.v1.html("""
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <script>
            const duration = 5 * 1000;
            const end = Date.now() + duration;
            const colors = ['#FF0000','#FF7F00','#FFFF00','#00FF00','#0000FF','#4B0082','#8B00FF'];
            (function frame() {
                confetti({particleCount: 5, angle: 60, spread: 55, origin: {x: 0, y: 0}, colors: colors});
                confetti({particleCount: 5, angle: 120, spread: 55, origin: {x: 1, y: 0}, colors: colors});
                if (Date.now() < end) {
                    requestAnimationFrame(frame);
                }
            })();
            </script>
            """, height=0, width=0)

        # Friendly URL
        st.markdown(
            f'<p style="text-align:center;color:white;font-size:16px">Share the raffle: {FRIENDLY_URL_HTML}</p>',
            unsafe_allow_html=True
        )
    else:
        st.info("No registrations yet")
