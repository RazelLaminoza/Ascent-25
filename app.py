import streamlit as st
import sqlite3
import random
import qrcode
import io
import pandas as pd
import base64
import time

# ---------------- DATABASE ----------------
conn = sqlite3.connect("raffle.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS entries (emp_number TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS winner (emp_number TEXT)""")
conn.commit()

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "register"
if "admin" not in st.session_state:
    st.session_state.admin = False

# ---------------- FUNCTIONS ----------------
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
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
        font-family: Helvetica, Arial, sans-serif;
    }}

    h1, h2, h3, p, label {{
        color: var(--text);
        font-family: Helvetica, Arial, sans-serif;
    }}

    .card {{
        background: rgba(255,255,255,0.15);
        padding: 25px;
        border-radius: 16px;
        backdrop-filter: blur(6px);
        max-width: 380px;
        margin: auto;
    }}

    .accent {{
        color: var(--accent);
        font-weight: bold;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg_local("bgna.png")

# ---------------- REGISTER PAGE ----------------
if st.session_state.page == "register":
    st.markdown("<h1 class='accent'>Register Here</h1>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    with st.form("register"):
        emp_number = st.text_input("Employee Number")
        submit = st.form_submit_button("Submit")

        if submit:
            if emp_number:
                c.execute("INSERT INTO entries VALUES (?)", (emp_number,))
                conn.commit()

                st.success("Registration successful!")
                qr = generate_qr(f"Employee Number: {emp_number}")
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf.getvalue())
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

    c.execute("SELECT emp_number FROM entries")
    entries = c.fetchall()

    if entries:
        df = pd.DataFrame(entries, columns=["Employee Number"])
        st.table(df)

        # Excel export
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
            slot.markdown(
                f"<h1 class='accent' style='font-size:90px'>{winner}</h1>",
                unsafe_allow_html=True
            )

    else:
        st.info("No registrations yet")

    if st.button("Logout"):
        st.session_state.page = "register"
        st.session_state.admin = False
