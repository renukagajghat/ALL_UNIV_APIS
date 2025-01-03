import fitz  # PyMuPDF
import os
from PIL import Image
import pytesseract
import re

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# File path of the PDF you want to extract images from
file_path = r"C:\APITEST\EDU-46740.pdf"

# Open the PDF file
try:
    pdf_file = fitz.open(file_path)
except Exception as e:
    print(f"[!] Failed to open the PDF file: {e}")
    exit()

# Create a directory to save images
output_dir = r"C:\APITEST\extracted_images"
os.makedirs(output_dir, exist_ok=True)

# Flag for the specific image we want to process
specific_image_name = "image_2_2.jpeg"  # Change extension to .jpeg
specific_image_path = os.path.join(output_dir, specific_image_name)

# Iterate over the PDF pages
for page_index in range(len(pdf_file)):
    # Get the page itself
    page = pdf_file.load_page(page_index)  # Load the page
    image_list = page.get_images(full=True)  # Get images on the page

    # Print the number of images found on this page
    if image_list:
        print(f"[+] Page {page_index + 1}: Found a total of {len(image_list)} images.")
    else:
        print(f"[!] Page {page_index + 1}: No images found.")

    for image_index, img in enumerate(image_list, start=1):
        try:
            # Get the XREF of the image
            xref = img[0]

            # Extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]

            # Get the image extension
            image_ext = 'jpeg'  # Change extension to jpeg
            image_name = f"image_{page_index + 1}_{image_index}.{image_ext}"  # Use .jpeg
            image_path = os.path.join(output_dir, image_name)  # Construct full path

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
                print(f"    [+] Image saved as {image_path}")

            # Check if the saved image is the specific one we want to process
            if image_name == specific_image_name:
                print(f"[+] Processing OCR on {specific_image_name}...")
                # Perform OCR on the specific saved image
                image = Image.open(image_path)

                # Perform OCR
                text = pytesseract.image_to_string(image)

                # Print extracted text
                if text.strip():  # Check if any text was extracted
                    print(f"[+] Extracted Text from {specific_image_name}:\n{text}\n")

                    # Generic regex patterns to capture names and CGPA
                    roll_number_pattern = r'Roll Mo:\s*(\d+)'  # Roll number pattern
                    name_pattern = r"Name:\s*(\d+)" #capture name
                    father_name_pattern = r"Father's name\s*.*?([A-Z\s]+)"  # Capture father's name
                    mother_name_pattern = r"Mother's name\s*.*?([A-Z\s]+)"  # Capture mother's name
                    cgpa_pattern = r'CGPA\s*:\s*(\d+\.\d+)|Overall.*CGPA\s*:\s*(\d+\.\d+)'  # Capture CGPA

                    # Extract the roll number
                    roll_number_match = re.search(roll_number_pattern, text)
                    roll_number = roll_number_match.group(1) if roll_number_match else 'Not found'

                    #extract the name
                    name_match = re.search(name_pattern,text)
                    name = name_match.group(1) if name_match else 'Not found'

                    # Extract father's name
                    father_name_match = re.search(father_name_pattern, text)
                    father_name = father_name_match.group(1).strip() if father_name_match else 'Not found'

                    # Extract mother's name
                    mother_name_match = re.search(mother_name_pattern, text)
                    mother_name = mother_name_match.group(1).strip() if mother_name_match else 'Not found'

                    # Extract CGPA
                    cgpa_match = re.search(cgpa_pattern, text)
                    cgpa = cgpa_match.group(1) if cgpa_match else (cgpa_match.group(2) if cgpa_match else 'Not found')

                    # Print extracted values
                    print(f"Roll Number: {roll_number}")
                    print(f"name: {name}")
                    print(f"Father Name: {father_name}")
                    print(f"Mother Name: {mother_name}")
                    print(f"CGPA: {cgpa}")

                else:
                    print(f"[!] No text extracted from {specific_image_name}.")

        except Exception as e:
            print(f"    [!] Failed to extract or save image {image_index} on page {page_index + 1}: {e}")

# Close the PDF file
pdf_file.close()
