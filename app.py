import streamlit as st
import sqlite3
import random
import qrcode
import io
import base64

# ---------------- SET BACKGROUND IMAGE ----------------
def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <style>
        /* Main page background */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Sidebar background */
        [data-testid="stSidebar"] {{
            background-color: rgba(255,255,255,0.8);
        }}
        /* Registration form container */
        .user-container {{
            background-color: transparent; /* fully transparent */
            padding: 30px;
            border-radius: 15px;
        }}
        /* Admin/Winner panel */
        .admin-container {{
            background-color: rgba(255,255,255,0.9); /* slightly opaque for readability */
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
        }}
        /* Text styling */
        h1, h2, h3, h4, .stText, .stMarkdown {{
            color: #fff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_local("bg.png")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("raffle.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS entries (
    name TEXT,
    emp_number TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS winner (
    name TEXT,
    emp_number TEXT
)
""")
conn.commit()

# ---------------- FUNCTIONS ----------------
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# ---------------- ROLE SELECTION ----------------
st.title("🎟 Welcome to Employee Raffle")
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

                # Generate QR code
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
    if "admin" not in st.session_state:
        st.session_state.admin = False

    st.markdown('<div class="admin-container">', unsafe_allow_html=True)
    st.subheader("Admin Login")

    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if (admin_user == st.secrets["ADMIN_USER"] and
            admin_pass == st.secrets["ADMIN_PASS"]):
            st.session_state.admin = True
            st.success("Admin logged in")
        else:
            st.error("Invalid admin credentials")

    # ---------------- ADMIN RAFFLE PANEL ----------------
    if st.session_state.admin:
        st.header("Admin Raffle Panel")

        c.execute("SELECT * FROM entries")
        entries = c.fetchall()
        st.write(f"Total entries: {len(entries)}")

        if st.button("Run Raffle"):
            if entries:
                winner = random.choice(entries)
                c.execute("DELETE FROM winner")
                c.execute("INSERT INTO winner VALUES (?, ?)", winner)
                conn.commit()
                st.success(f"Winner: {winner[0]} (Employee Number: {winner[1]})")
            else:
                st.error("No entries yet")

        # ---------------- SHOW WINNER ----------------
        st.divider()
        st.subheader("Winner")
        c.execute("SELECT * FROM winner")
        winner = c.fetchone()

        if winner:
            st.success(f"{winner[0]} (Employee Number: {winner[1]})")
        else:
            st.info("No winner selected yet")
    st.markdown('</div>', unsafe_allow_html=True)
