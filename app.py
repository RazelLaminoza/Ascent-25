import streamlit as st
import sqlite3
import random
import qrcode
import io
import pandas as pd
import base64
import time

# ---------------- CONFIG ----------------
EXPIRY_DAYS = 15
NOW_TS = int(time.time())
EXPIRY_TS = NOW_TS - (EXPIRY_DAYS * 24 * 60 * 60)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("raffle.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS entries (
    emp_number TEXT UNIQUE,
    created_at INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS winner (
    emp_number TEXT,
    created_at INTEGER
)
""")

# Auto-delete expired records
c.execute("DELETE FROM entries WHERE created_at < ?", (EXPIRY_TS,))
c.execute("DELETE FROM winner WHERE created_at < ?", (EXPIRY_TS,))
conn.commit()

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin" not in st.session_state:
    st.session_state.admin = False

# ---------------- FUNCTIONS ----------------
def generate_qr(data):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    :root {{
        --accent: #c2185b;
        --text: #111;
    }}

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: Helvetica, Arial, sans-serif;
    }}

    h1, h2, h3, p, label {{
        font-family: Helvetica, Arial, sans-serif;
        color: var(--text);
    }}

    .card {{
        background: rgba(255,255,255,0.22);
        padding: 25px;
        border-radius: 18px;
        backdrop-filter: blur(8px);
        max-width: 380px;
        margin: auto;
    }}

    .accent {{
        color: var(--accent);
        text-align: center;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg_local("bgna.png")

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown("<h1 class='accent'>Welcome</h1>", unsafe_allow_html=True)
    st.image("welcome_photo.png", use_column_width=True)

    st.markdown("""
    <div class="card">
        <p><strong>Venue:</strong> Okada Manila Ballroom 1–3</p>
        <p><strong>Date:</strong> January 25, 2026</p>
        <p><strong>Time:</strong> 5:00 PM</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Register Here"):
        st.session_state.page = "register"

# ---------------- REGISTRATION PAGE ----------------
elif st.session_state.page == "register":
    st.markdown("<h1 class='accent'>Register Here</h1>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    with st.form("register_form"):
        emp_number = st.text_input("Employee Number")
        submit = st.form_submit_button("Submit")

        if submit:
            if emp_number:
                try:
                    c.execute(
                        "INSERT INTO entries VALUES (?, ?)",
                        (emp_number, int(time.time()))
                    )
                    conn.commit()

                    st.success("Registration successful!")

                    qr = generate_qr(f"Employee Number: {emp_number}")
                    buf = io.BytesIO()
                    qr.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="Your QR Code")

                except sqlite3.IntegrityError:
                    st.warning("Employee number already registered")
            else:
                st.error("Employee Number is required")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Admin Login"):
        st.session_state.page = "admin"

# ---------------- ADMIN LOGIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h2 class='accent'>Admin Login</h2>", unsafe_allow_html=True)

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == st.secrets["ADMIN_USER"] and pwd == st.secrets["ADMIN_PASS"]:
            st.session_state.admin = True
            st.session_state.page = "raffle"
        else:
            st.error("Invalid credentials")

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":
    st.markdown("<h1 class='accent'>🎲 Raffle Draw</h1>", unsafe_allow_html=True)

    c.execute(
        "SELECT emp_number FROM entries WHERE created_at >= ?",
        (EXPIRY_TS,)
    )
    entries = c.fetchall()

    if entries:
        df = pd.DataFrame(entries, columns=["Employee Number"])
        st.table(df)

        excel = io.BytesIO()
        df.to_excel(excel, index=False)
        excel.seek(0)
        st.download_button(
            "Download Excel",
            excel,
            "registered_employees.xlsx"
        )

        if st.button("Run Raffle"):
            slot = st.empty()
            for _ in range(30):
                slot.markdown(
                    f"<h1 class='accent'>{random.choice(entries)[0]}</h1>",
                    unsafe_allow_html=True
                )
                time.sleep(0.05)

            winner = random.choice(entries)[0]
            c.execute("DELETE FROM winner")
            c.execute(
                "INSERT INTO winner VALUES (?, ?)",
                (winner, int(time.time()))
            )
            conn.commit()

            slot.markdown(
                f"<h1 class='accent' style='font-size:90px'>{winner}</h1>",
                unsafe_allow_html=True
            )
    else:
        st.info("No valid registrations (older than 15 days auto-removed)")

    if st.button("Logout"):
        st.session_state.page = "landing"
        st.session_state.admin = False
