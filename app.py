import streamlit as st
import pandas as pd
import random
import os
import io
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import qrcode

st.markdown("""
<style>
/* FULL KIOSK LOCKDOWN */

/* Hide Streamlit top-right toolbar (fork, rerun, settings) */
[data-testid="stToolbar"] {
    display: none !important;
}

/* Hide floating deploy / fork button */
[data-testid="stDeployButton"] {
    display: none !important;
}

/* Hide hamburger menu */
#MainMenu {
    visibility: hidden;
}

/* Hide footer */
footer {
    visibility: hidden;
}

/* Hide header bar */
header {
    visibility: hidden;
}

/* Lock scrolling */
html, body {
    overflow: hidden !important;
    height: 150%;
}

/* Remove Streamlit padding */
.block-container {
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

def shuffle_effect(df):
    placeholder = st.empty()

    # shuffle effect
    for _ in range(20):
        name = random.choice(df["Full Name"].tolist())
        placeholder.markdown(
            f"<h2 style='text-align:center; color:#FFD700;'>{name}</h2>",
            unsafe_allow_html=True
        )
        time.sleep(0.05)

    # final winner
    winner = random.choice(df["Full Name"].tolist())
    st.session_state.winner = winner
    placeholder.markdown(
        f"<h2 style='text-align:center; color:#FFD700;'>{winner}</h2>",
        unsafe_allow_html=True
    )


def add_custom_font():
    font_path = "PPNeueMachina-PlainUltrabold.ttf"

    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            font_b64 = base64.b64encode(f.read()).decode()

        st.markdown(f"""
            <style>
                @font-face {{
                    font-family: "PPNeueMachina";
                    src: url("data:font/ttf;base64,{font_b64}") format("truetype");
                }}

                /* Apply font everywhere in Streamlit */
                * {{
                    font-family: "PPNeueMachina" !important;
                }}

                /* Extra strong override for Streamlit internal elements */
                [class*="css"] {{
                    font-family: "PPNeueMachina" !important;
                }}

                /* Buttons and Inputs */
                button, input, textarea, select {{
                    font-family: "PPNeueMachina" !important;
                }}
            </style>
        """, unsafe_allow_html=True)

add_custom_font()

# ---------------------------
# Constants
# ---------------------------
DATA_FILE = "registered.csv"
EMPLOYEE_EXCEL = "clean_employees.xlsx"

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
# HIDE STREAMLIT UI + LOCK SCROLL
# ---------------------------
def hide_streamlit_ui():
    st.markdown("""
        <style>
            /* LOCK SCROLL */
            html, body {
                overflow: hidden !important;
            }

            /* HIDE STREAMLIT MENU (TOP RIGHT) */
            #MainMenu {visibility: hidden;}

            /* HIDE FOOTER */
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


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
# Image Resize Fix
# ---------------------------
def resize_keep_aspect(img, max_size):
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img


# ---------------------------
# QR & Pass Image
# ---------------------------
def generate_qr(data):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def create_pass_image(name, emp, qr_img):
    bg = Image.open("bgna.png").convert("RGBA")
    bg = bg.resize((900, 500))

    img = Image.new("RGBA", (900, 500))
    img.paste(bg, (0, 0))

    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("CourierPrime-Bold.ttf", 42)
        font_small = ImageFont.truetype("CourierPrime-Bold.ttf", 26)
    except:
        font_big = font_small = ImageFont.load_default()

    text_color = (255, 255, 255, 255)

    logo1 = Image.open("1.png").convert("RGBA")
    logo2 = Image.open("2.png").convert("RGBA")

    logo1 = resize_keep_aspect(logo1, (120, 120))
    logo2 = resize_keep_aspect(logo2, (120, 120))

    img.paste(logo1, (620, 30), logo1)
    img.paste(logo2, (760, 30), logo2)

    draw.text((40, 40), "ASCENT APAC 2026", fill=text_color, font=font_big)
    draw.text((40, 120), "FULL NAME:", fill=text_color, font=font_big)
    draw.text((40, 160), name, fill=text_color, font=font_small)

    draw.text((40, 260), "EMPLOYEE NO:", fill=text_color, font=font_small)
    draw.text((40, 300), emp, fill=text_color, font=font_big)

    draw.text(
        (40, 380),
        "Present this pre-registration pass\nat the check-in counter",
        fill=text_color,
        font=font_small
    )

    qr_img = qr_img.resize((220, 220))
    img.paste(qr_img, (620, 140), qr_img.convert("RGBA"))

    return img.convert("RGB")


# ---------------------------
# Main App
# ---------------------------
def main():
    load_custom_font()
    set_background()
    hide_streamlit_ui()  # <<-- HERE

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
    img2_b64 = base64.b64encode(open("2.png", "rb").read()).decode()
    img1_b64 = base64.b64encode(open("1.png", "rb").read()).decode()

    st.markdown("""
    <style>
    .landing {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        text-align: center;
        opacity: 0.95;
    }

    .landing img {
        margin: 10px;
    }

    .landing p {
        font-size: 18px;
        line-height: 1.3;
        color: white;
    }

    .landing span {
        font-size: 16px;
    }

    .stButton button {
        width: 360px !important;
        height: 55px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        background-color: #FFD700 !important;
        color: black !important;
        border: none !important;
        border-radius: 8px !important;
        margin-top: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="landing">
            <img src="data:image/png;base64,{img2_b64}" width="200" />
            <img src="data:image/png;base64,{img1_b64}" width="450" />
            <p>
                PRE-REGISTER NOW AND TAKE PART IN THE RAFFLE<br>
                <span>January 25, 2026 | OKADA BALLROOM 1–3</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Pre-register"):
        set_page("register")


# ---------------------------
# Register Page
# ---------------------------
def register_page():
    st.markdown("<h1 style='text-align:center;'>Register</h1>", unsafe_allow_html=True)

    with st.form(key="register_form"):
        emp_id = st.text_input("Type employee id number", key="register_emp_id")
        submit = st.form_submit_button("Submit")

    if submit:

        if emp_id == "admin123":
            set_page("admin")
            return

        if not os.path.exists(EMPLOYEE_EXCEL):
            st.error("Employee Excel file not found.")
            return

        df_employees = pd.read_excel(EMPLOYEE_EXCEL)

        if emp_id not in df_employees["emp"].astype(str).tolist():
            st.error("Employee ID NOT VERIFIED ")
            return

        df_reg = load_registered()

        if emp_id in df_reg["emp_id"].astype(str).tolist():
            st.error("You have already registered")
            return

        name = df_employees[df_employees["emp"].astype(str) == emp_id]["name"].values[0]

        new_row = pd.DataFrame([{"name": name, "emp_id": emp_id}])
        df_reg = pd.concat([df_reg, new_row], ignore_index=True)
        save_registered(df_reg)

        qr_img = generate_qr(f"{name} | {emp_id}")
        pass_img = create_pass_image(name, emp_id, qr_img)

        buf = io.BytesIO()
        pass_img.save(buf, format="PNG")
        pass_bytes = buf.getvalue()

        st.success("Registered and VERIFIED ✔️")
        img_b64 = base64.b64encode(pass_bytes).decode()

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

    with st.form(key="admin_form"):
        user = st.text_input("User", key="admin_user")
        pwd = st.text_input("Password", type="password", key="admin_pwd")
        submit = st.form_submit_button("Login")

    if submit:
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

def set_background():
    with open("bgna.png", "rb") as f:  # your background image
        data = f.read()
    b64 = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# Raffle Page (SAFE LONG SHUFFLE)
# ---------------------------
def main():
    # ---------- BIG TITLE (CENTERED) ----------
    st.markdown(
        "<h1 style='font-size: 30px; text-align:center;'>RAFFLE WINNER</h1>",
        unsafe_allow_html=True
    )

    df = load_registered()

    if df.empty:
        st.warning("No entries yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return  # <-- OK because we are inside main()

    if "raffle_name" not in st.session_state:
        st.session_state.raffle_name = "Press Draw Winner"

    placeholder = st.empty()

    # ---------- BIG NAME DISPLAY (CENTERED) ----------
    placeholder.markdown(
        f"<h2 style='color:#FFD700; font-size: 60px; text-align:center;'>{st.session_state.raffle_name}</h2>",
        unsafe_allow_html=True
    )

    # ---------- BACK BUTTON ----------
    if st.button("⬅ Back", key="raffle_back_btn"):
        set_page("admin")

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
