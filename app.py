import streamlit as st
import sqlite3
import random
import qrcode
import io
import base64
import pandas as pd

# ---------------- SET BACKGROUND IMAGE ----------------
def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(255,255,255,0.8);
        }}
        .user-container {{
            background-color: transparent;
            padding: 30px;
            border-radius: 15px;
        }}
        .admin-container {{
            background-color: rgba(255,255,255,0.9);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
        }}
        .landing-text {{
            position: absolute;
            top: 30%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: white;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
        }}
        .landing-button button {{
            font-size: 20px;
            padding: 10px 30px;
            border-radius: 10px;
            background-color: #FF4B4B;
            color: white;
            border: none;
            cursor: pointer;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background
set_bg_local("welcome_photo.png")  # Your landing page photo

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "entries" not in st.session_state:
    st.session_state.entries = []
if "winner" not in st.session_state:
    st.session_state.winner = None
if "admin" not in st.session_state:
    st.session_state.admin = False

# ---------------- FUNCTIONS ----------------
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# ---------------- DATABASE ----------------
conn = sqlite3.connect("raffle.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS entries (name TEXT, emp_number TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS winner (name TEXT, emp_number TEXT)""")
conn.commit()

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown(
        """
        <div class="landing-text">
            <h1>🎉 Welcome to the Employee Raffle!</h1>
            <p><strong>Venue:</strong> Okada Manila Ballroom 1-3</p>
            <p><strong>Date:</strong> January 25, 2026</p>
            <p><strong>Time:</strong> 5:00 PM</p>
            <div class="landing-button">
                <button onclick="window.location.reload()">Proceed</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Smooth transition: when the button is clicked, change page state
    if st.button("Proceed"):
        st.session_state.page = "main"

# ---------------- MAIN PAGE (Role Selection) ----------------
elif st.session_state.page == "main":
    st.title("🎟 Employee Raffle")
    role = st.radio("Are you a User or Admin?", ["User", "Admin"])

    # ---------------- USER REGISTRATION ----------------
    if role == "User":
        st.markdown('<div class="user-container">', unsafe_allow_html=True)
        st.subheader("Employee Registration")

        with st.form("register_form"):
            name = st.text_input("Name")
            emp_number = st.text_input("Employee Number")
            submit = st.form_submit_button("Submit")

            if submit:
                if name and emp_number:
                    c.execute("INSERT INTO entries VALUES (?, ?)", (name, emp_number))
                    conn.commit()
                    st.success("You are registered!")

                    qr_data = f"Name: {name}\nEmployee Number: {emp_number}"
                    qr_img = generate_qr(qr_data)
                    buf = io.BytesIO()
                    qr_img.save(buf, format="PNG")
                    buf.seek(0)
                    st.image(buf, caption="Your QR Code")
                else:
                    st.error("Please fill in all fields")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- ADMIN LOGIN ----------------
    elif role == "Admin":
        st.markdown('<div class="admin-container">', unsafe_allow_html=True)
        st.subheader("🔐 Admin Login")

        admin_user = st.text_input("Admin Username")
        admin_pass = st.text_input("Admin Password", type="password")

        if st.button("Login"):
            if (admin_user == st.secrets["ADMIN_USER"] and
                admin_pass == st.secrets["ADMIN_PASS"]):
                st.session_state.admin = True
                st.success("Admin logged in")
            else:
                st.error("Invalid admin credentials")

        # ---------------- ADMIN PANEL ----------------
        if st.session_state.admin:
            st.header("🎉 Admin Raffle Panel")
            c.execute("SELECT * FROM entries")
            entries = c.fetchall()

            if entries:
                st.subheader("📋 Registered Employees")
                df = pd.DataFrame(entries, columns=["Name", "Employee Number"])
                st.table(df)

                # Download Excel
                excel_bytes = io.BytesIO()
                df.to_excel(excel_bytes, index=False, engine='openpyxl')
                excel_bytes.seek(0)
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_bytes,
                    file_name="raffle_entries.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Run raffle
                if st.button("🎲 Run Raffle"):
                    winner = random.choice(entries)
                    c.execute("DELETE FROM winner")
                    c.execute("INSERT INTO winner VALUES (?, ?)", winner)
                    conn.commit()
                    st.success(f"Winner: {winner[0]} (Employee Number: {winner[1]})")
            else:
                st.info("No entries yet")

            # Show winner
            st.divider()
            st.subheader("🏆 Winner")
            c.execute("SELECT * FROM winner")
            winner = c.fetchone()
            if winner:
                st.success(f"{winner[0]} (Employee Number: {winner[1]})")
            else:
                st.info("No winner selected yet")

        st.markdown('</div>', unsafe_allow_html=True)
