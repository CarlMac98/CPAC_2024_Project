import os
import base64
import requests
import qrcode
from PIL import Image
# === CONFIGURATION ===
API_KEY = "cac6be150bcf68a28cfcc68198cf2fba"
IMAGE_PATH = r"C:\Users\franc\OneDrive - Politecnico di Milano\Secondo anno\Creative programming\CPAC_2024_Project\TouchDesigner\stylized_image.jpg"  # replace with your local image file
QR_PATH    = r"C:\Users\franc\OneDrive - Politecnico di Milano\Secondo anno\Creative programming\CPAC_2024_Project\TouchDesigner\upload_qr.png"

def upload_image_and_generate_qr():
    # === STEP 1: Read & Base64-encode the image ===
    with open(IMAGE_PATH, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

    # === STEP 2: Build the request ===
    endpoint = "https://api.imgbb.com/1/upload"
    payload = {
        "key": API_KEY,
        "image": encoded_string,
        # optional: "expiration": 600  # auto-delete after 600 seconds
    }

    # === STEP 3: Send the POST ===
    response = requests.post(endpoint, data=payload)
    response.raise_for_status()   # will raise an exception for HTTP errors

    # === STEP 4: Parse & print the URL ===
    data = response.json()
    if data.get("success"):
        direct_url = data["data"]["url"]          # e.g. https://i.ibb.co/…
        viewer_url = data["data"]["url_viewer"]   # e.g. https://ibb.co/…
        print("Direct image URL: ", direct_url)
        print("Viewer URL:      ", viewer_url)
        # === STEP 4: Generate a QR code for the direct URL ===
        # Install prerequisite: pip install qrcode[pil]
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(direct_url)
        qr.make(fit=True)

        # img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(), fill_color="white", back_color="black")
        qr_img = qr.make_image(fill_color="white", back_color="black",)
        # === CREATE 1280×720 CANVAS AND CENTER QR ===
        canvas_w, canvas_h = 1280, 720
        canvas = Image.new("RGB", (canvas_w, canvas_h), "black")

        # Resize QR to fit nicely (e.g. max 80% of the smaller canvas dimension)
        max_qr_size = int(min(canvas_w, canvas_h) * 1.2)
        qr_img = qr_img.resize((max_qr_size, max_qr_size), Image.NEAREST)

        # Compute top-left coords to center
        x = (canvas_w - max_qr_size) // 2
        y = (canvas_h - max_qr_size) // 2
        canvas.paste(qr_img, (x, y))

        # === SAVE OUT ===
        canvas.save(QR_PATH)
    else:
        print("Upload failed:", data)
