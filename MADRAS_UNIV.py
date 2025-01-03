import os
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import cv2
from pyzbar.pyzbar import decode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import mysql.connector

app = Flask(__name__)


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

# Function to extract the second image from each page of the PDF and save it
def convert_pdf_to_images(pdf_file_path, output_dir="pdf_images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_file = fitz.open(pdf_file_path)
    image_paths = []

    # Iterate over the pages of the PDF
    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)  # Load the page
        image_list = page.get_images(full=True)  # Get images on the page

        # Check if the page has images
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images on page {page_index}")
        else:
            print(f"[!] No images found on page {page_index}")

        # Only extract the second image if available (index 1)
        if len(image_list) > 1:
            img = image_list[1]  # Get the second image (index 1)
            xref = img[0]  # Get the XREF of the image

            # Extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]

            # Get the image extension
            image_ext = base_image["ext"]

            # Save the second image
            image_name = f"{output_dir}/image{page_index + 1}_2.{image_ext}"
            with open(image_name, "wb") as image_file:
                image_file.write(image_bytes)
                image_paths.append(image_name)
                print(f"[+] Image saved as {image_name}")

    return image_paths

# Function to decode the QR code from an image
def decode_qr_code(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        print("Error loading image.")
        return None

    # Resize image for better detection
    resized_image = cv2.resize(image, (1200, 900))

    # Decode the QR code using pyzbar
    decoded_objects = decode(resized_image)
    if decoded_objects:
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            print("QR Code Detected with pyzbar:", data)
            return data
    else:
        print("No QR code found with pyzbar.")
        return None

# Function to setup Selenium WebDriver
def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    driver_service = Service(executable_path='C:/Users/renuka/chromedriver.exe')  # Adjust path to chromedriver
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    return driver

# Function to fetch result and save a screenshot
def fetch_result_from_url(qr_code_data):
    try:
        driver = setup_selenium()
        driver.get(qr_code_data)  # Open the URL
        time.sleep(5)  # Allow the page to load

        # Find the result element (adjust XPath based on your specific page structure)
        result_text = driver.find_element(By.XPATH, "//h5[@class='sizevar']").text

        # Save a screenshot of the page
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Format: "YYYY-MM-DD-HH-MM-SS"
        screenshot_filename = f"madras_univ_result_{timestamp}.png"  # Append form # Append timestamp to filename
        save_page_screenshot(driver, screenshot_filename)

        # Save the filename and other details to the database
        save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

        driver.quit()
        return result_text, screenshot_filename
    except Exception as e:
        print(f"Error fetching result: {e}")
        if driver:
            driver.quit()
        return None, None

# Flask API endpoint to handle PDF processing
@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    file = request.files['file']
    if not file:
        return jsonify({"error": "No file provided"}), 400

    try:
        # Save the uploaded file temporarily
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Step 1: Extract images from the PDF
        image_paths = convert_pdf_to_images(file_path)
        if not image_paths:
            return jsonify({"error": "No second image found in the PDF"}), 400

        # Step 2: Decode QR code from the second image
        qr_code_data = None
        for image_path in image_paths:
            qr_code_data = decode_qr_code(image_path)
            if qr_code_data:
                break

        if not qr_code_data:
            return jsonify({"error": "QR code not found in the second image"}), 400

        # Step 3: Fetch result and screenshot from the QR code's URL
        result_text, screenshot_path = fetch_result_from_url(qr_code_data)
        if not result_text or not screenshot_path:
            return jsonify({"error": "Failed to fetch result from URL"}), 400

        # Return the result and screenshot path to the client
        return jsonify({"message": "Success", "result": result_text, "screenshot": screenshot_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('pdf_images'):
        os.makedirs('pdf_images')

    app.run(debug=True)
