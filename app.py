import streamlit as st
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
        h1, h2, h3, h4, .stText, .stMarkdown {{
            color: #fff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set your background image here
set_bg_local("bg.png")

# ---------------- SESSION STATE INIT ----------------
if "entries" not in st.session_state:
    st.session_state.entries = []  # list of tuples (name, emp_number)
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
                st.session_state.entries.append((name, emp_number))
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

        if st.session_state.entries:
            st.subheader("📋 Registered Employees")
            st.table(st.session_state.entries)  # show entries directly

            # ---------- DOWNLOAD AS EXCEL ----------
            df = pd.DataFrame(st.session_state.entries, columns=["Name", "Employee Number"])
            excel_bytes = io.BytesIO()
            df.to_excel(excel_bytes, index=False, engine='openpyxl')
            excel_bytes.seek(0)

            st.download_button(
                label="📥 Download as Excel",
                data=excel_bytes,
                file_name="raffle_entries.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # ---------- RUN RAFFLE ----------
            if st.button("🎲 Run Raffle"):
                winner = random.choice(st.session_state.entries)
                st.session_state.winner = winner
                st.success(f"Winner: {winner[0]} (Employee Number: {winner[1]})")
        else:
            st.info("No entries yet")

        # Show winner
        st.divider()
        st.subheader("🏆 Winner")
        if st.session_state.winner:
            st.success(f"{st.session_state.winner[0]} (Employee Number: {st.session_state.winner[1]})")
        else:
            st.info("No winner selected yet")
    st.markdown('</div>', unsafe_allow_html=True)
