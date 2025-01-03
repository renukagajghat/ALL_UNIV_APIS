from PIL import Image
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image = Image.open('254811.jpg')

text = pytesseract.image_to_string(image)

print("Extracted Text:\n", text)

# Regex to capture the roll number and name
roll_number_pattern = r'Roll No\.\s*(\d+)'  
name_pattern = r'Roll No\.\s*\d+\s*\n([A-Z\s]+)\n'

# Extract the roll number
roll_number_match = re.search(roll_number_pattern, text)
roll_number = roll_number_match.group(1) if roll_number_match else 'Not found'

# Extract the name 
name_match = re.search(name_pattern, text)
name = name_match.group(1).strip() if name_match else 'Not found'

# extract father's name
father_name_match = re.search(r"Father's name\s*\n([A-Z\s]+)\n", text)
father_name = father_name_match.group(1).strip().split("\n")[0] if father_name_match else 'Not found'


mother_name_match = re.search(r"Father's name\s*\n[A-Z\s]+\n([A-Z\s]+)\n", text)
if 'other' in text.lower():
    mother_name = mother_name_match.group(1).strip() if mother_name_match else 'Not found'
else:
    mother_name = 'Not found'

# Extract CGPA 
cgpa_match = re.search(r'Overall\s*:\s*CGPA\s*:\s*(\d+\.\d+)', text)
cgpa = cgpa_match.group(1) if cgpa_match else 'Not found'

print(f"Roll Number: {roll_number}")
print(f"Name: {name}")
print(f"Father Name: {father_name}")
print(f"Mother Name: {mother_name}")
print(f"CGPA: {cgpa}")
