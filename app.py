if st.session_state.page == "register":
    st.markdown("<h1 style='color:white;'>Register Here</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            max-width: 520px !important;
            height: 55px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            background-color: #FFD700 !important;
            color: black !important;
            border: none !important;
            border-radius: 8px !important;
            margin: 0 auto !important;
            padding: 0 !important;
        }

        div[data-testid="stFormSubmitButton"] > button span,
        div[data-testid="stFormSubmitButton"] > button span * {
            color: black !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ------------------ PASS PREVIEW (SHOW BEFORE FORM) ------------------
    if st.session_state.get("pass_bytes"):
        st.image(
            st.session_state.pass_bytes,
            caption="✅ Your Pass Preview",
            width=700
        )

        st.download_button(
            "📥 Download Pass (PNG)",
            st.session_state.pass_bytes,
            file_name=f"{st.session_state.pass_emp}_event_pass.png",
            mime="image/png",
            type="primary",
            key="download_pass"
        )

    # ------------------ FORM ------------------
    with st.form("form_register"):
        emp = st.text_input("Employee ID", key="emp_input")
        submit = st.form_submit_button("Submit", type="primary", key="submit_register")

        if submit:
            if emp == "admin123":
                st.session_state.go_admin = True

            elif not emp:
                st.error("Employee ID NOT VERIFIED ❌")

            elif any(e["emp"] == emp for e in st.session_state.entries):
                st.error("You already registered ❌")

            elif emp not in st.session_state.valid_employees:
                st.error("Employee ID NOT VERIFIED ❌")

            else:
                name = st.session_state.valid_employees.get(emp, "Unknown")
                st.session_state.entries.append({"emp": emp, "Full Name": name})

                # SAVE DATA FUNCTION (YOUR FUNCTION)
                save_data()

                # GENERATE QR & PASS IMAGE (YOUR FUNCTIONS)
                qr_img = generate_qr(f"{name} | {emp}")
                pass_img = create_pass_image(name, emp, qr_img)

                buf = io.BytesIO()
                pass_img.save(buf, format="PNG")
                pass_bytes = buf.getvalue()

                st.session_state.pass_bytes = pass_bytes
                st.session_state.pass_emp = emp

                st.success("Registered and VERIFIED ✔️")

                # CLEAR EMPLOYEE ID AFTER SUCCESS
                st.session_state.emp_input = ""

# -------------------- REDIRECT TO ADMIN --------------------
if st.session_state.get("go_admin", False):
    st.session_state.go_admin = False
    st.session_state.emp_input = ""   # CLEAR EMPLOYEE ID
    go_to("admin")
