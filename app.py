import qrcode
from PIL import Image
import io

# Example function
def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# In the registration form
if submit:
    if name and email:
        c.execute("INSERT INTO entries VALUES (?, ?)", (name, email))
        conn.commit()
        st.success("You are registered!")
        
        # Generate QR
        qr_data = f"Name: {name}\nEmail: {email}"
        qr_img = generate_qr(qr_data)
        st.image(qr_img, caption="Your QR Code")
