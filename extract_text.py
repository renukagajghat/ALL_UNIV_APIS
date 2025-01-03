import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re

# Set Tesseract OCR path
pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path to the PDF (modify this to the correct path)
pdf_path = 'C:/Users/Administrator/Documents/EDU-52908.pdf'

def extract_exam_and_roll_no(pdf_path):
    # Open the PDF with PyMuPDF
    doc = fitz.open(pdf_path)

    # Iterate over the pages
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)

        # Convert page to image (increase DPI for better clarity)
        pix = page.get_pixmap(dpi=600)  # Use 600 DPI for better clarity
        img_path = f"page_{page_number + 1}_image.png"
        pix.save(img_path)

        # Open the image for preprocessing
        img = Image.open(img_path)

        # Apply preprocessing to enhance the image
        img = img.convert("L")  # Convert to grayscale
        img = img.filter(ImageFilter.MedianFilter(size=3))  # Remove noise
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(3)  # Enhance contrast
        img = img.filter(ImageFilter.SHARPEN)  # Apply sharpening
        img = img.point(lambda x: 0 if x < 200 else 255, '1')  # Adaptive thresholding for better clarity

        preprocessed_img_path = f"page_{page_number + 1}_preprocessed_image.png"
        img.save(preprocessed_img_path)

        # Extract text with Tesseract (use a custom config for better results)
        ocr_text = pytesseract.image_to_string(img, config='--psm 6')  # Use PSM 6 for uniform blocks

        # Split the OCR text into lines
        lines = ocr_text.split("\n")
        exam_line = None
        roll_no = None

        for line in lines:
            # Search for line with 'EXAM'
            if "exam" in line.lower() and not exam_line:
                exam_line = line
            # Search for line with 'Roll No.'
            if "roll no" in line.lower() and not roll_no:
                roll_no = line

            # If both lines are found, break out of loop
            if exam_line and roll_no:
                break

        # Print the results
        if exam_line:
            print(f"Found line with 'EXAM': {exam_line}")
        else:
            print("No line found containing 'EXAM'.")

        if roll_no:
            print(f"Found line with 'Roll No.': {roll_no}")
        else:
            print("No line found containing 'Roll No.'")

    # Close the PDF document
    doc.close()

# Run the function on the specific PDF
extract_exam_and_roll_no(pdf_path)
