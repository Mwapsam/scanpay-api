import base64
import os
import qrcode
import io
from PIL import Image
from django.conf import settings


def generate_qr_code(data, size=10, border=0):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    return img


def generate_qr(url_text):
    generated_code = generate_qr_code(data=url_text, size=10, border=1)
    bio = io.BytesIO()
    img_save = generated_code.save(bio)
    png_qr = bio.getvalue()
    base64qr = base64.b64encode(png_qr)
    img_name = base64qr.decode("utf-8")
    context_dict = dict()
    context_dict["file_type"] = "png"
    context_dict["image_base64"] = img_name
    return context_dict


def convert_base64(base64_str, id):
    decoded_data = base64.b64decode(base64_str)

    img = Image.open(io.BytesIO(decoded_data))

    file_name = f"{id}-image.png"
    file_path = os.path.join(settings.MEDIA_ROOT, "qr_codes", file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    img.save(file_path)

    return os.path.join("qr_codes", file_name)
