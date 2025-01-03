from flask import Flask, request, jsonify
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
import pytesseract
import time
import fitz  # PyMuPDF
import io
import re
from autocorrect import Speller  # Import the autocorrect library
import mysql.connector
import os

# Set the path to the Tesseract OCR executable (update with your path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize the spell checker
spell = Speller()

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")  # Optional: Run in headless mode
chrome_options.add_argument("--disable-web-security")  # Optional: Disable web security

# Setup the WebDriver (ensure you have the correct path to ChromeDriver)
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

app = Flask(__name__)

# Upload directory
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_filename_to_db(username, password, filename):
    """Save login details and the filename into the database."""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="education_schema"
        )
        cursor = connection.cursor()

        # Insert data into the table, including the filename
        insert_query = """
        INSERT INTO login_details (login_value, password_value, filename)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (username, password, filename))

        # Commit the transaction
        connection.commit()
        print(f"Data saved successfully with file {filename}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_page_html(driver, filename):
    """Save the page HTML source."""
    page_source = driver.page_source
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(page_source)
    print(f"Page source saved as {filename}")

def save_page_screenshot(driver, filename):
    """Save a screenshot of the page."""
    driver.save_screenshot(filename)
    print(f"Screenshot saved as {filename}")

def login_to_website(driver, username, password):
    """Login to the website and handle CAPTCHA."""
    driver.get('https://tsche1.com/verifyTss/reglog/login.php')
    wait = WebDriverWait(driver, 120)

    # Step 1: Enter username
    username_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    username_field.send_keys(username)

    # Step 2: Enter password
    password_field = driver.find_element(By.NAME, 'password')
    password_field.send_keys(password)

    # Step 3: Handle CAPTCHA
    captcha_input = driver.find_element(By.NAME, 'captcha_code')
    driver.save_screenshot('full_page_screenshot.png')
    location = captcha_input.location_once_scrolled_into_view
    size = captcha_input.size

    # Process CAPTCHA image
    image = Image.open('full_page_screenshot.png')
    left = location['x']
    top = location['y']
    right = left + size['width']
    bottom = top + size['height']
    captcha_image = image.crop((left, top, right, bottom))
    captcha_image = captcha_image.convert('L')
    captcha_image = captcha_image.point(lambda p: p > 128 and 255)
    captcha_image = captcha_image.resize((captcha_image.width * 2, captcha_image.height * 2), Image.LANCZOS)
    captcha_text = pytesseract.image_to_string(captcha_image, config='--oem 3 --psm 6').strip()

    # Step 4: Enter CAPTCHA text
    captcha_input.send_keys(captcha_text)

    # Step 5: Submit the login form
    submit_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.NAME, 'submit'))
    )
    submit_button.click()

    # Wait for the next page to load
    time.sleep(5)

def select_university(driver, university_name):
    """Select university from the dropdown."""
    dropdown_container = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'list-group-item'))
    )

    # Locate and select the university
    dropdown_items = driver.find_elements(By.CLASS_NAME, 'list-group-item')

    # Normalize the extracted university name (remove extra spaces and make it lowercase)
    normalized_university_name = university_name.strip().lower()

    print(f"Normalized extracted university name: '{normalized_university_name}'")  # Debug print

    for item in dropdown_items:
        # Clean the item text (remove extra spaces and make it lowercase)
        item_text = item.text.strip().lower()

        # Remove the leading number and dot (if any) at the start
        cleaned_item_text = re.sub(r'^\d+\.\s*', '', item_text)

        # Remove commas and handle case insensitivity
        cleaned_item_text = cleaned_item_text.replace(",", "").strip()

        # Print cleaned dropdown item for debugging
        print(f"Cleaned dropdown item: '{cleaned_item_text}'")  # Debug print

        # Check if the normalized university name is a substring of the cleaned item text
        if normalized_university_name in cleaned_item_text:
            print(f"Selecting university: {item.text.strip()}")
            item.click()
            return

    print(f"University '{university_name}' not found in the dropdown list.")

def enter_degree_details(driver, degree, year, seat_no):
    try:
        # Step 7: Select degree from the dropdown
        degree_dropdown = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, 'degree'))
        )
        
        # Matching the degree with the option values
        degree_dict = {
            "B.Pharmacy": "bpharm",
            "B.Tech": "btech",
            "M.B.A.": "mba",
            "MCA": "mca",
            "M.Pharmacy": "mpharm",
            "M.Tech": "mtech"
        }
        
        normalized_degree = degree.strip()
        degree_value = degree_dict.get(normalized_degree, None)
        
        if degree_value:
            # Select the corresponding degree option
            for option in degree_dropdown.find_elements(By.TAG_NAME, 'option'):
                if option.get_attribute("value") == degree_value:
                    option.click()
                    break
        else:
            print(f"Degree '{degree}' not found in the dropdown.")

        # Step 8: Select year from the dropdown
        year_dropdown = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, 'year_passed'))
        )
        for option in year_dropdown.find_elements(By.TAG_NAME, 'option'):
            if year.strip() in option.text.strip():
                option.click()
                break

        # Step 9: Enter the Hall Ticket No.
        seat_no_field = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, 'usr_htno'))
        )
        seat_no_field.send_keys(seat_no)

        # Step 10: Wait for the Submit button to be clickable and then click
        submit_button = WebDriverWait(driver, 180).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        
        # Move to the submit button to make sure it is in view, then click
        ActionChains(driver).move_to_element(submit_button).click().perform()

        # Wait for the page heading to appear after submission
        WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.XPATH, "//h2[text()='TSCHE:: Student Academic Verification Service']"))
        )

        # Save the page content as HTML and as a screenshot
        save_page_html(driver, "submission_result.html")
        # Get current timestamp in the desired format
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Format: "YYYY-MM-DD-HH-MM-SS"
        screenshot_filename = f"submission_result_{timestamp}.png"  # Append form # Append timestamp to filename
        save_page_screenshot(driver, screenshot_filename)

        # Save the filename and other details to the database
        save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

    except Exception as e:
        print(f"Error during form submission: {str(e)}")  # Capture and print any exceptions that occur
        driver.quit()


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using OCR if necessary."""
    document = fitz.open(pdf_path)
    full_text = ""

    for page_number in range(document.page_count):
        page = document.load_page(page_number)
        text = page.get_text("text")

        if text:
            full_text += text
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))
            img = Image.open(io.BytesIO(pix.tobytes()))
            img = img.convert('L')
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
            text = pytesseract.image_to_string(img, config='--psm 3')
            full_text += text

    return full_text

def extract_specific_details(text):
    """Extract university name, degree (from predefined list), year of final exam (only year), hall ticket number, and name."""
    # Regular expressions to find the required information
    university_name_pattern = r"(DR\. B\. R\. AMBEDKAR OPEN UNIVERSITY HYDERABAD|JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD|KAKATIYA UNIVERSITY WARANGAL|MAHATMA GANDHI UNIVERSITY NALGONDA|OSMANIA UNIVERSITY HYDERABAD|PALAMURU UNIVERSITY MAHABUBNAGAR|RAJIV GANDHI UNIVERSITY OF KNOWLEDGE TECHNOLOGIES BASARA|SATAVAHANA UNIVERSITY KARIMNAGAR|TELANGANA UNIVERSITY NIZAMABAD|JAWAHARLAL NEHRU ARCHITECTURE AND FINE ARTS UNIVERSITY HYDERABAD|POTTI SREERAMULU TELUGU UNIVERSITY HYDERABAD|PROF\. JAYASHANKAR STATE AGRICULTURE UNIVERSITY RAJENDRANAGAR HYD|SRI PV NARSIMHA RAO STATE STATE UNIVERSITY OF VETERINARY ANIMAL AND FISHERY SCIENCES HYD|SRI KONDA LAXMAN TELANGANA STATE HORTICULTURE UNIVERSITY BUDWEL HYD|SRI\. KALOJI NARAYAN RAO UNIVERSITY OF HEALTH SCIENCES)"
    degree_pattern = r"\b(B\.?Pharmacy|B\.?Tech\.?|M\.?B\.?A|MCA|M\.?Pharmacy|M\.?Tech\.?)\b"
    hall_ticket_number_pattern = r"Hall Ticket No\.\s*(\S+)"  # Match alphanumeric hall ticket numbers
    name_pattern = r"Name\s*:\s*([A-Za-z\s]+)"  # Pattern for name extraction

    # Perform regex search for university, degree, year of exam, and name
    university_name = re.search(university_name_pattern, text)
    degree = re.search(degree_pattern, text)
    year_match = re.search(r'\b(20\d{2})\b', text)
    name = re.search(name_pattern, text)

    # Extract all occurrences of Hall Ticket No.
    hall_ticket_numbers = re.findall(hall_ticket_number_pattern, text)

    # If there are multiple hall ticket numbers, select the last one
    if hall_ticket_numbers:
        hall_ticket_number = hall_ticket_numbers[-1]  # Last occurrence
    else:
        hall_ticket_number = None

    # Create a dictionary to store the results
    extracted_details = {}

    # Add extracted details to the dictionary if found
    if university_name:
        extracted_details['University Name'] = university_name.group(0)
    
    # Add the degree if found
    if degree:
        extracted_details['Degree'] = degree.group(0)
    
    if hall_ticket_number:
        extracted_details['Hall Ticket Number'] = hall_ticket_number  # Last hall ticket number
    
    if year_match:
        extracted_details['Year of Final Exam'] = year_match.group(0)  # Capture only the year
    
    if name:
        extracted_details['Name'] = name.group(1).strip()  # Name without extra spaces

    return extracted_details


@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Accept PDF file from POST request."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # Save the uploaded file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Process the uploaded PDF
        text = extract_text_from_pdf(pdf_path)
        extracted_details = extract_specific_details(text)

        # Print extracted details for verification
        print("Extracted Details:")
        for key, value in extracted_details.items():
            print(f"{key}: {value}")

        # Initialize WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            username = 'finance@mistitservices.com'
            password = '1234mkM#'

            # Login to the website
            login_to_website(driver, username, password)

            # Dynamically assign values from the extracted details
            university_name = extracted_details.get('University Name', '')
            degree = extracted_details.get('Degree', '')
            year = extracted_details.get('Year of Final Exam', '')
            seat_no = extracted_details.get('Hall Ticket Number', '')

            if not university_name or not degree or not year or not seat_no:
                return jsonify({"error": "Missing required details from the PDF."}), 400

            # Select university from the dropdown and enter degree details
            select_university(driver, university_name)
            enter_degree_details(driver, degree, year, seat_no)

            return jsonify({"message": "Result generated successfully!"})

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            driver.quit()

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(debug=True)

