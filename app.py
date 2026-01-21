import streamlit as st
import pandas as pd
import random
import base64
import os
from PIL import Image, ImageDraw, ImageFont
import io

# ---------------------------
# Constants
# ---------------------------
DATA_FILE = "registered.csv"
EMPLOYEE_EXCEL = "employee_list.xlsx"

# ---------------------------
# Custom Font
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
            html, body, [class*="css"]  {{
                font-family: "PPNeue";
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

# ---------------------------
# Main App
# ---------------------------
def main():
    load_custom_font()

    if "page" not in st.session_state:
        st.session_state.page = "landing"

    if st.session_state.page == "landing":
        landing_page()

    elif st.session_state.page == "register":
        register_page()

    elif st.session_state.page == "admin":
        admin_page()


# ---------------------------
# Landing Page
# ---------------------------
def landing_page():
    st.markdown("<h1 style='text-align:center;'>Welcome</h1>", unsafe_allow_html=True)

    # Image 2 (Top Center)
    st.image("image2.png", use_column_width=False, width=300)

    # Center Image 1
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image("image1.png", use_column_width=False, width=350)
    st.markdown("</div>", unsafe_allow_html=True)

    # Rounded button to Register
    if st.button("Go to Register", key="landing_to_register"):
        set_page("register")


# ---------------------------
# Register Page
# ---------------------------
def register_page():
    st.markdown("<h1 style='text-align:center;'>Register</h1>", unsafe_allow_html=True)

    emp_id = st.text_input("Type employee id number")

    # Button style using CSS
    st.markdown("""
    <style>
    .round-btn button {
        border-radius: 15px;
        width: 100%;
        height: 50px;
        font-size: 18px;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Submit", key="register_submit"):
        # Load excel list
        if not os.path.exists(EMPLOYEE_EXCEL):
            st.error("Employee Excel file not found.")
            return

        df_employees = pd.read_excel(EMPLOYEE_EXCEL)

        # Check if ID exists
        if emp_id not in df_employees["EmployeeID"].astype(str).tolist():
            st.error("Invalid ID")
            return

        # Check if already registered
        df_reg = load_registered()
        if emp_id in df_reg["emp_id"].astype(str).tolist():
            st.error("Already used")
            return

        # Save record
        name = df_employees[df_employees["EmployeeID"].astype(str) == emp_id]["Name"].values[0]
        df_reg = df_reg.append({"name": name, "emp_id": emp_id}, ignore_index=True)
        save_registered(df_reg)

        # Show card + download PNG
        show_card(name, emp_id)

        st.success("Registration successful!")

    if st.button("Back to Landing"):
        set_page("landing")

# ---------------------------
# Card & Download PNG
# ---------------------------
def show_card(name, emp_id):
    img = Image.new("RGB", (600, 350), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("PPNeueMachina-PlainUltrabold.ttf", 40)

    draw.text((50, 100), f"Name: {name}", font=font, fill=(0,0,0))
    draw.text((50, 180), f"ID: {emp_id}", font=font, fill=(0,0,0))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    st.image(img, width=500)

    st.download_button(
        label="Download PNG",
        data=buffer,
        file_name="badge.png",
        mime="image/png"
    )

# ---------------------------
# Admin Page
# ---------------------------
def admin_page():
    st.markdown("<h1 style='text-align:center;'>Admin Login</h1>", unsafe_allow_html=True)

    user = st.text_input("User")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.success("Login Successful!")
            show_admin_table()
        else:
            st.error("Invalid credentials")

    if st.button("Back to Landing"):
        set_page("landing")


def show_admin_table():
    st.markdown("<h2>Registered Users</h2>", unsafe_allow_html=True)

    df = load_registered()
    st.dataframe(df)

    if st.button("Enter Raffle"):
        raffle(df)

# ---------------------------
# Raffle Shuffle
# ---------------------------
def raffle(df):
    if df.empty:
        st.warning("No entries yet.")
        return

    names = df["name"].tolist()
    st.write("Shuffling...")
    random.shuffle(names)

    for n in names:
        st.markdown(f"<h3 style='text-align:center;'>{n}</h3>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
