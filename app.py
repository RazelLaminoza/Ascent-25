import streamlit as st
import sqlite3
import random
import qrcode
from PIL import Image
import io
import smtplib
from email.message import EmailMessage

# ---------------- DATABASE ----------------
conn = sqlite3.connect("raffle.db", check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute("""
CREATE TABLE IF NOT EXISTS entries (
    name TEXT,
    email TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS winner (
    name TEXT,
    email TEXT
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

def send_email(to_email, subject, body, qr_image):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = st.secrets["EMAIL_USER"]
    msg['To'] = to_email
    msg.set_content(body)

    # Convert QR PIL image to bytes
    buf = io.BytesIO()
    qr_image.save(buf, format='PNG')
    buf.seek(0)
    msg.add_attachment(buf.read(), maintype='image', subtype='png', filename='qr.png')

    # Connect to Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
        smtp.send_message(msg)

# ---------------- USER REGISTRATION ----------------
st.title("🎟 Event Registration")

with st.form("register_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    submit = st.form_submit_button("Submit")

    if submit:
        if name and email:
            # Save to database
            c.execute("INSERT INTO entries VALUES (?, ?)", (name, email))
            conn.commit()
            st.success("You are registered!")

            # Generate QR code
            qr_data = f"Name: {name}\nEmail: {email}"
            qr_img = generate_qr(qr_data)

            # Convert PIL image to BytesIO for Streamlit Cloud
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, caption="Your QR Code")

            # Send QR via email
            try:
                send_email(
                    to_email=email,
                    subject="Your Event QR Code",
                    body=f"Hi {name},\n\nHere is your QR code for the event.",
                    qr_image=qr_img
                )
                st.success("QR code sent to your email!")
            except Exception as e:
                st.error(f"Failed to send email: {e}")
        else:
            st.error("Please fill in all fields")

# ---------------- ADMIN LOGIN ----------------
st.divider()
st.subheader("🔐 Admin Login")

if "admin" not in st.session_state:
    st.session_state.admin = False

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
    st.header("🎉 Admin Raffle Panel")

    c.execute("SELECT * FROM entries")
    entries = c.fetchall()
    st.write(f"Total entries: {len(entries)}")

    if st.button("🎲 Run Raffle"):
        if entries:
            winner = random.choice(entries)
            c.execute("DELETE FROM winner")
            c.execute("INSERT INTO winner VALUES (?, ?)", winner)
            conn.commit()
            st.success(f"Winner: {winner[0]} ({winner[1]})")
        else:
            st.error("No entries yet")

# ---------------- SHOW WINNER ----------------
st.divider()
st.subheader("🏆 Winner")

c.execute("SELECT * FROM winner")
winner = c.fetchone()

if winner:
    st.success(f"{winner[0]} ({winner[1]})")
else:
    st.info("No winner selected yet")
