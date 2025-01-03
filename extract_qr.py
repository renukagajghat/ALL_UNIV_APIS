import fitz  # PyMuPDF
from pyzbar.pyzbar import decode
from PIL import Image
import io

def extract_qr_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        decoded_objects = decode(img)
        for obj in decoded_objects:
            print(f"QR Code detected: {obj.data.decode('utf-8')}")
            return obj.data.decode('utf-8')

    return "No QR Code found"

# Use your PDF file path
pdf_path = "C:/Users/Administrator/Downloads/EDU-52882_1.pdf"
print(extract_qr_from_pdf(pdf_path))
