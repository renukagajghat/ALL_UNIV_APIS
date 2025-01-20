
# *********************API for captch extraction and saved into db**************************

from flask import Flask, request, jsonify
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pytesseract
from mysql.connector import connect, Error

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if needed



# Initialize Flask app
app = Flask(__name__)

# Your MySQL connection details
DB_HOST = 'your_db_host'
DB_USER = 'your_db_user'
DB_PASSWORD = 'your_db_password'
DB_NAME = 'your_db_name'

# Setup Selenium WebDriver (Chrome)
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = None

# Create connection function for MySQL
def create_connection():
    try:
        conn = connect(
            host="localhost",
            user="root",
            password="",
            database="education_schema"
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

driver = None
@app.route('/login', methods=['POST'])
def login():
    driver = None

    try:
        # Get login details from the request
        login_value = request.json['login_value']
        password_value = request.json['password_value']

        # Initialize WebDriver
        service = Service('C:/Users/renuka/chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)

        # Navigate to the login page
        driver.get("https://tsche1.com/verifyTss/reglog/login.php")
        time.sleep(5)  # Adjust the wait as needed for the page to load

        # Enter email
        email_input = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        email_input.send_keys(login_value)

        # Enter password
        password_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        password_input.send_keys(password_value)

        # Handle CAPTCHA
        captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, "captcha_code")))

        # Screenshot and image processing
        driver.save_screenshot('full_page_screenshot.png')
        location = captcha_input.location_once_scrolled_into_view
        size = captcha_input.size
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

        # Fill in the CAPTCHA and submit form
        captcha_input.send_keys(captcha_text)
        # submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        # submit_button.click()

        # Wait for the next page to load (dummy content for example)
        time.sleep(3)
        list_group_content = '<div>list group div 2</div>'

        # Insert data into MySQL
        conn = create_connection()
        if conn:
            try:
                cur = conn.cursor()
                insert_query = """INSERT INTO login_details (login_value, password_value, captcha_text, list_group_content) 
                                  VALUES (%s, %s, %s, %s)"""
                values = (login_value, password_value, captcha_text, list_group_content)
                cur.execute(insert_query, values)
                conn.commit()
                response = {"status": "success", "message": "Data inserted successfully"}
            except Error as e:
                response = {"status": "error", "message": f"MySQL Error: {e}"}
            finally:
                conn.close()
        else:
            response = {"status": "error", "message": "Could not connect to the database"}

    except Exception as e:
        response = {"status": "error", "message": f"An unexpected error occurred: {e}"}

    finally:
        if driver:
            driver.quit()
        else:
            print("driver was not initialised...")    

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
