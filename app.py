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
c.execute("""CREATE TABLE IF NOT EXISTS entries (name TEXT, emp_number TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS winner (name TEXT, emp_number TEXT)""")
conn.commit()

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin" not in st.session_state:
    st.session_state.admin = False

# ---------------- FUNCTIONS ----------------
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def set_bg_local(image_file):
    """Set background image with professional fonts and transparent forms."""
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(255,255,255,0.0);
        }}
        h1, h2, h3, h4, .stText, .stMarkdown {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #b00000;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        .center-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            margin-top: 20px;
        }}
        .form-container {{
            background-color: rgba(255,255,255,0.0);
            padding: 0px;
            border-radius: 0px;
            box-shadow: none;
            width: 350px;
        }}
        .landing-text {{
            text-align:center;
            color: #b00000;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin-top: 20px;
            font-size: 18px;
        }}
        .landing-button button {{
            font-size: 18px;
            padding: 10px 25px;
            border-radius: 8px;
            background-color: #b00000;
            color: white;
            border: none;
            cursor: pointer;
        }}
        </style>
    """, unsafe_allow_html=True)

# Apply background
set_bg_local("bgna.png")

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.title("Welcome to the Employee Raffle")
    st.image("welcome_photo.png", use_column_width=True)
    st.markdown("""
        <div class="landing-text">
            <p><strong>Venue:</strong> Okada Manila Ballroom 1-3</p>
            <p><strong>Date:</strong> January 25, 2026</p>
            <p><strong>Time:</strong> 5:00 PM</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Proceed to Registration / Admin Login"):
        st.session_state.page = "login"

# ---------------- LOGIN / REGISTRATION PAGE ----------------
elif st.session_state.page == "login":
    st.title("Employee Raffle Portal")
    role = st.radio("Select Role", ["User", "Admin"])
    st.markdown('<div class="center-container">', unsafe_allow_html=True)

    if role == "User":
        st.subheader("Employee Registration")
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        with st.form("register_form"):
            name = st.text_input("Name")
            emp_number = st.text_input("Employee Number")
            submit = st.form_submit_button("Submit")
            if submit:
                if name and emp_number:
                    c.execute("INSERT INTO entries VALUES (?, ?)", (name, emp_number))
                    conn.commit()
                    st.success("Registration successful!")
                    qr_data = f"Name: {name}\nEmployee Number: {emp_number}"
                    qr_img = generate_qr(qr_data)
                    buf = io.BytesIO()
                    qr_img.save(buf, format="PNG")
                    buf.seek(0)
                    st.image(buf, caption="Your QR Code")
                else:
                    st.error("Please complete all fields")
        st.markdown('</div>', unsafe_allow_html=True)

    elif role == "Admin":
        st.subheader("Admin Login")
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if (admin_user == st.secrets["ADMIN_USER"] and admin_pass == st.secrets["ADMIN_PASS"]):
                st.session_state.admin = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.admin:
            if st.button("Go to Raffle Page"):
                st.session_state.page = "raffle"

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":
    st.title("🎲 Raffle Draw")
    c.execute("SELECT * FROM entries")
    entries = c.fetchall()

    if entries:
        df = pd.DataFrame(entries, columns=["Name", "Employee Number"])
        st.subheader("Registered Employees")
        st.table(df)

        if st.button("Run Shuffle Raffle"):
            placeholder = st.empty()
            winner_name = ""
            # Shuffle animation
            for _ in range(30):
                winner_name = random.choice(entries)[0]
                placeholder.markdown(f"<h2 style='color:#b00000'>{winner_name}</h2>", unsafe_allow_html=True)
                time.sleep(0.05)
            # Commit winner
            winner = random.choice(entries)
            c.execute("DELETE FROM winner")
            c.execute("INSERT INTO winner VALUES (?, ?)", winner)
            conn.commit()
            placeholder.markdown(f"<h2 style='color:#b00000'>Winner: {winner[0]}</h2>", unsafe_allow_html=True)
    else:
        st.info("No entries yet. Please register employees first.")

    if st.button("Back to Admin Panel"):
        st.session_state.page = "login"
