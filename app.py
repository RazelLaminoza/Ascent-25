import streamlit as st
import sqlite3
import random

# ---------------- DATABASE ----------------
# Connect to SQLite (Streamlit Cloud stores in RAM, small events are fine)
conn = sqlite3.connect("raffle.db", check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
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

# ---------------- USER REGISTRATION ----------------
st.title("🎟 Event Registration")

with st.form("register_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    submit = st.form_submit_button("Submit")

    if submit:
        if name and email:
            c.execute("INSERT INTO entries VALUES (?, ?)", (name, email))
            conn.commit()
            st.success("You are registered!")
        else:
            st.error("Please fill in all fields")

# ---------------- ADMIN LOGIN ----------------
st.divider()
st.subheader("🔐 Admin Login")

# Use session_state to track admin login
if "admin" not in st.session_state:
    st.session_state.admin = False

admin_user = st.text_input("Admin Username")
admin_pass = st.text_input("Admin Password", type="password")

if st.button("Login"):
    if (
        admin_user == st.secrets["ADMIN_USER"]
        and admin_pass == st.secrets["ADMIN_PASS"]
    ):
        st.session_state.admin = True
        st.success("Logged in as Admin")
    else:
        st.error("Invalid admin credentials")

# ---------------- ADMIN RAFFLE PANEL ----------------
if st.session_state.admin:
    st.header("🎉 Admin Raffle Panel")

    # Fetch all entries
    c.execute("SELECT * FROM entries")
    entries = c.fetchall()

    st.write(f"Total entries: {len(entries)}")

    if st.button("🎲 Run Raffle"):
        if entries:
            # Pick a random winner
            winner = random.choice(entries)
            # Save winner
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
