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

# Load entries from file
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
    <style>
    :root {{
        --accent: #c2185b;
        --text: #ffffff;
    }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: Helvetica, Arial, sans-serif;
    }}
    h1, h2, h3 {{
        font-family: Helvetica, Arial, sans-serif;
        color: white;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    .card {{
        background: rgba(255,255,255,0.2);
        padding: 25px;
        border-radius: 18px;
        backdrop-filter: blur(8px);
        max-width: 400px;
        margin: 20px auto;
        box-shadow: none;
    }}
    .accent {{
        text-align: center;
        font-weight: bold;
    }}
    .rainbow {{
        animation: rainbow 2s linear infinite;
        font-size: 90px;
        font-weight: bold;
        text-align:center;
    }}
    @keyframes rainbow {{
        0%{{color:#FF0000;}}
        14%{{color:#FF7F00;}}
        28%{{color:#FFFF00;}}
        42%{{color:#00FF00;}}
        57%{{color:#0000FF;}}
        71%{{color:#4B0082;}}
        85%{{color:#8B00FF;}}
        100%{{color:#FF0000;}}
    }}
    /* ---------- FORM STYLING ---------- */
    div.stTextInput > label, 
    div.stTextInput > div > input, 
    div.stTextInput > div > div > input,
    div.stTextInput > div > textarea {{
        color: white !important;
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 16px;
        font-family: Helvetica, Arial, sans-serif;
    }}
    div.stTextInput > label {{
        color: white !important;
        font-weight: 600;
    }}
    div.stTextInput > div > input:focus, 
    div.stTextInput > div > div > input:focus,
    div.stTextInput > div > textarea:focus {{
        outline: none;
        border: 2px solid var(--accent);
        background: rgba(255,255,255,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg_local("bgna.png")

# ---------------- LANDING PAGE ----------------
if st.session_state.page == "landing":
    st.markdown("<h1>Welcome</h1>", unsafe_allow_html=True)
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
    st.markdown("<h1>Register Here</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Admin Login"):
        st.session_state.page = "admin"

# ---------------- ADMIN LOGIN ----------------
elif st.session_state.page == "admin":
    st.markdown("<h2>Admin Login</h2>", unsafe_allow_html=True)
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("⬅ Back to Register"):
        st.session_state.page = "register"
    if st.button("Login"):
        if user == st.secrets["ADMIN_USER"] and pwd == st.secrets["ADMIN_PASS"]:
            st.session_state.admin = True
            st.session_state.page = "raffle"
        else:
            st.error("Invalid credentials")

# ---------------- RAFFLE PAGE ----------------
elif st.session_state.page == "raffle":
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
        df = pd.DataFrame(entries)
        st.table(df)
        excel = io.BytesIO()
        df.to_excel(excel, index=False)
        excel.seek(0)
        st.download_button("Download Excel", excel, "registered_employees.xlsx")

        # -------- WINNER ANIMATION WITH DYNAMIC CONFETTI --------
        if st.button("Run Raffle"):
            placeholder = st.empty()
            for _ in range(30):
                current = random.choice(entries)
                placeholder.markdown(
                    f"<h1 style='color:white;font-size:70px'>{current['name']} ({current['emp_number']})</h1>",
                    unsafe_allow_html=True
                )
                time.sleep(0.07)

            winner = random.choice(entries)
            st.session_state.winner = winner
            save_data()

            # Rainbow winner
            placeholder.markdown(
                f"<div class='rainbow'>{winner['name']} ({winner['emp_number']})</div>",
                unsafe_allow_html=True
            )

            # Dynamic rainbow confetti
            confetti_html = """
            <div id="confetti-container"></div>
            <script>
            const colors = ['#FF0000','#FF7F00','#FFFF00','#00FF00','#0000FF','#4B0082','#8B00FF'];
            for(let i=0;i<100;i++){
                let div = document.createElement('div');
                div.className = 'confetti-piece';
                div.style.left = Math.random() * window.innerWidth + 'px';
                div.style.backgroundColor = colors[Math.floor(Math.random()*colors.length)];
                div.style.animationDuration = (Math.random() * 3 + 2) + 's';
                div.style.width = div.style.height = (Math.random() * 8 + 4) + 'px';
                document.body.appendChild(div);
            }
            setTimeout(()=>{document.getElementById('confetti-container').remove()}, 4000);
            </script>
            """
            st.components.v1.html(confetti_html, height=0, width=0)

    else:
        st.info("No registrations yet")
