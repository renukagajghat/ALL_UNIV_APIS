import fitz  # PyMuPDF
import cv2
import io
import numpy as np
import pytesseract
from PIL import Image

# Set the Tesseract executable path (adjust this to your setup)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Path to the PDF file
pdf_path = 'C:/Users/Administrator/Downloads/17/EDU-51864.pdf'

# Function to preprocess the image for better OCR
def preprocess_image(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

# Function to extract text from an image
def extract_text_from_image(image):
    # Tesseract config for better OCR (adjust psm and oem as needed)
    config = '--oem 3 --psm 6 -l eng'
    return pytesseract.image_to_string(image, config=config)

# Open the PDF and extract images
document = fitz.open(pdf_path)
all_text = ""  # Store all text for readable format

for page_num in range(len(document)):
    print(f"Processing page {page_num + 1}...")
    page = document.load_page(page_num)
    
    # Convert PDF page to image
    pixmap = page.get_pixmap(dpi=300)
    image = Image.open(io.BytesIO(pixmap.tobytes()))
    
    # Preprocess the image
    processed_image = preprocess_image(image)
    
    # OCR to extract text
    text = extract_text_from_image(processed_image)
    all_text += f"Page {page_num + 1}:\n{text}\n{'-' * 50}\n"  # Append page text
    
    # Save preprocessed image for debugging (optional)
    cv2.imwrite(f"processed_page_{page_num + 1}.jpg", processed_image)

# Save the full text to a file
output_text_path = 'extracted_text.txt'
with open(output_text_path, 'w', encoding='utf-8') as f:
    f.write(all_text)

print(f"Text extraction complete. Saved to {output_text_path}.")
