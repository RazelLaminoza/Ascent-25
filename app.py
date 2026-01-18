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

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.entries = data.get("entries", [])
else:
    st.session_state.entries = []

if "valid_employees" not in st.session_state:
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

# ---------------- UTILITIES ----------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"entries": st.session_state.entries}, f)

def save_employees():
    with open(EMPLOYEE_FILE, "w") as f:
        json.dump(st.session_state.valid_employees, f)

def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_bg(image_file):
    encoded = get_image_base64(image_file)
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    /* Hide default Streamlit headers */
    header, footer, [data-testid="stToolbar"] {{
        visibility: hidden;
    }}
    .stButton button {{
        width: 100%;
        border-radius: 25px;
        height: 50px;
        font-weight: bold;
        text-transform: uppercase;
    }}
    div[data-testid="stForm"] {{
        background: rgba(0,0,0,0.5);
        border-radius: 15px;
        padding: 20px;
        color: white;
    }}
    h1, p {{
        color: white;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIC ----------------
def go_to(page_name):
    st.session_state.page = page_name

def run_raffle():
    if st.session_state.entries:
        st.session_state.winner = random.choice(st.session_state.entries)

# ---------------- NAVIGATION ----------------
set_bg("bgna.png")

# --- LANDING PAGE ---
if st.session_state.page == "landing":
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Centered Logos and Text
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{get_image_base64('2.png')}" width="120">
            <br><br>
            <img src="data:image/png;base64,{get_image_base64('1.png')}" style="width: 80%; max-width: 800px;">
            <p style="font-size: 24px; margin-top: 20px;">PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE</p>
            <p style="font-size: 16px; opacity: 0.8;">January 25, 2026 | OKADA BALLROOM 1–3</p>
        </div>
    """, unsafe_allow_html=True)

    # Use columns to center the Streamlit button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("Register", on_click=go_to, args=("register",), type="primary")

# --- REGISTER PAGE ---
elif st.session_state.page == "register":
    st.markdown("<h1>Registration</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("reg_form"):
            emp_id = st.text_input("Enter Employee ID")
            submitted = st.form_submit_button("Verify & Register")
            
            if submitted:
                if emp_id in st.session_state.valid_employees:
                    # Check if already registered
                    if any(e['emp'] == emp_id for e in st.session_state.entries):
                        st.warning("You are already registered!")
                    else:
                        name = st.session_state.valid_employees[emp_id]
                        st.session_state.entries.append({"emp": emp_id, "name": name})
                        save_data()
                        st.success(f"Welcome, {name}! You are registered.")
                else:
                    st.error("Employee ID not found.")
        
        st.button("Back", on_click=go_to, args=("landing",))

# --- ADMIN PANEL ---
elif st.session_state.page == "admin":
    st.markdown("<h1>Admin Management</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # File Upload for Employee List
        uploaded_file = st.file_uploader("Update Employee Database (Excel)", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            # Expecting columns 'EMP ID' and 'Full Name'
            st.session_state.valid_employees = df.set_index("EMP ID")["Full Name"].to_dict()
            save_employees()
            st.success("Database Updated!")

        if st.button("Go to Raffle Draw"):
            go_to("raffle")
        st.button("Back to Home", on_click=go_to, args=("landing",))

# --- RAFFLE PAGE ---
elif st.session_state.page == "raffle":
    st.markdown("<h1>Raffle Draw</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎰 SPIN THE WHEEL", type="primary"):
            run_raffle()
        
        if st.session_state.winner:
            st.markdown(f"""
                <div style="background: rgba(255, 215, 0, 0.2); border: 2px solid gold; border-radius: 20px; padding: 20px; margin-top: 20px;">
                    <h2 style="color: gold;">WINNER</h2>
                    <h1 style="font-size: 50px;">{st.session_state.winner['name']}</h1>
                    <p>ID: {st.session_state.winner['emp']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.button("Back", on_click=go_to, args=("landing",))
