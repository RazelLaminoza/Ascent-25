import streamlit as st
import pandas as pd
import random
import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import qrcode

# ---------------------------
# Constants
# ---------------------------
DATA_FILE = "registered.csv"
EMPLOYEE_EXCEL = "employee_list.xlsx"

# ---------------------------
# Custom Font + Background
# ---------------------------
def load_custom_font():
    font_path = "PPNeueMachina-PlainUltrabold.ttf"
    if os.path.exists(font_path):
        st.markdown(
            f"""
            <style>
            @font-face {{
                font-family: "PPNeue";
                src: url("{font_path}");
            }}
            html, body, [class*="css"] {{
                font-family: "PPNeue";
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

def set_background():
    image_path = "bgna.png"
    if not os.path.exists(image_path):
        return

    with open(image_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------
# Data
# ---------------------------
def load_registered():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["name", "emp_id"])

def save_registered(df):
    df.to_csv(DATA_FILE, index=False)

# ---------------------------
# Navigation
# ---------------------------
def set_page(page_name):
    st.session_state.page = page_name
    if page_name != "admin":
        st.session_state.admin_logged_in = False

# ---------------------------
# QR & Pass Image
# ---------------------------
def generate_qr(data):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def create_pass_image(name, emp_id, qr_img):
    img = Image.new("RGB", (700, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("PPNeueMachina-PlainUltrabold.ttf", 40)

    draw.text((50, 120), f"Name: {name}", font=font, fill=(0,0,0))
    draw.text((50, 200), f"ID: {emp_id}", font=font, fill=(0,0,0))

    # Add QR
    qr_img = qr_img.resize((180, 180))
    img.paste(qr_img, (480, 150))

    return img

# ---------------------------
# Main App
# ---------------------------
def main():
    load_custom_font()
    set_background()

    if "page" not in st.session_state:
        st.session_state.page = "landing"

    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "register":
        register_page()
    elif st.session_state.page == "admin":
        admin_page()
    elif st.session_state.page == "raffle":
        raffle_page()

# ---------------------------
# Landing Page
# ---------------------------
def landing_page():
    st.markdown("<h1 style='text-align:center;'>Welcome</h1>", unsafe_allow_html=True)

    # Top Center Image
    if os.path.exists("2.png"):
        st.image("2.png", width=300)

    # Center Image
    if os.path.exists("1.png"):
        st.image("1.png", width=350)

    if st.button("Go to Register"):
        set_page("register")

# ---------------------------
# Register Page
# ---------------------------
def register_page():
    st.markdown("<h1 style='text-align:center;'>Register</h1>", unsafe_allow_html=True)

    emp_id = st.text_input("Type employee id number", key="register_emp_id")

    if st.button("Submit", key="register_submit_btn"):

        # ---- ADMIN SECRET CODE ----
        if emp_id == "admin123":
            set_page("admin")
            return

        if not os.path.exists(EMPLOYEE_EXCEL):
            st.error("Employee Excel file not found.")
            return

        df_employees = pd.read_excel(EMPLOYEE_EXCEL)

        # Validation using emp column
        if emp_id not in df_employees["emp"].astype(str).tolist():
            st.error("Employee ID NOT VERIFIED ❌")
            return

        df_reg = load_registered()

        # Already used?
        if emp_id in df_reg["emp_id"].astype(str).tolist():
            st.error("Employee ID NOT VERIFIED ❌")
            return

        name = df_employees[df_employees["emp"].astype(str) == emp_id]["name"].values[0]

        # Add to registered list
        new_row = pd.DataFrame([{"name": name, "emp_id": emp_id}])
        df_reg = pd.concat([df_reg, new_row], ignore_index=True)
        save_registered(df_reg)

        # ----- CREATE PASS IMAGE -----
        qr_img = generate_qr(f"{name} | {emp_id}")
        pass_img = create_pass_image(name, emp_id, qr_img)

        buf = io.BytesIO()
        pass_img.save(buf, format="PNG")
        pass_bytes = buf.getvalue()

        st.success("Registered and VERIFIED ✔️")
        img_b64 = base64.b64encode(pass_bytes).decode()

        # ----- SHOW PASS IN STYLED BOX -----
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

        # ------------------ DOWNLOAD BUTTON ------------------
        st.download_button(
            "📥 Download Pass (PNG)",
            pass_bytes,
            file_name=f"{emp_id}_event_pass.png",
            mime="image/png",
            key="download_pass_btn"
        )

    if st.button("Back", key="register_back_btn"):
        set_page("landing")


# ---------------------------
# Admin Page
# ---------------------------
def admin_page():
    st.markdown("<h1 style='text-align:center;'>Admin Login</h1>", unsafe_allow_html=True)

    if st.session_state.get("admin_logged_in", False):
        show_admin_table()
        return

    user = st.text_input("User", key="admin_user")
    pwd = st.text_input("Password", type="password", key="admin_pwd")

    if st.button("Login", key="admin_login_btn"):
        if user == "admin" and pwd == "admin123":
            st.success("Login Successful!")
            st.session_state.admin_logged_in = True
            show_admin_table()
        else:
            st.error("Invalid credentials")

    if st.button("Back", key="admin_back_btn"):
        set_page("landing")


def delete_all_entries():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.success("All entries deleted!")

def delete_entry(emp_id):
    df = load_registered()
    df = df[df["emp_id"].astype(str) != str(emp_id)]
    save_registered(df)
    st.success(f"Deleted entry: {emp_id}")

def show_admin_table():
    st.markdown("<h2>Registered Users</h2>", unsafe_allow_html=True)
    df = load_registered()
    st.dataframe(df)

    emp_to_delete = st.text_input("Enter employee ID to delete", key="delete_emp")
    if st.button("Delete Entry", key="delete_entry_btn"):
        if emp_to_delete.strip() == "":
            st.error("Please enter an employee ID")
        else:
            delete_entry(emp_to_delete)

    if st.button("Delete All Entries", key="delete_all_btn"):
        delete_all_entries()

    if st.button("Enter Raffle", key="raffle_btn"):
        set_page("raffle")

    if st.button("Back", key="admin_table_back_btn"):
        set_page("landing")


# ---------------------------
# Raffle Page (Only 1 Name)
# ---------------------------
def raffle_page():
    st.markdown("<h1 style='text-align:center;'>Raffle</h1>", unsafe_allow_html=True)

    df = load_registered()
    if df.empty:
        st.warning("No entries yet.")
        return

    if st.button("Draw Winner", key="draw_winner_btn"):
        winner = random.choice(df["name"].tolist())
        st.markdown(f"<h2 style='text-align:center; color:#FFD700;'>{winner}</h2>", unsafe_allow_html=True)

    if st.button("Back", key="raffle_back_btn"):
        set_page("admin")


if __name__ == "__main__":
    main()
