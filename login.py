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

# Flask app setup
app = Flask(__name__)

# Path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Setup Selenium WebDriver (Chrome)
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")  # Optional: Run in headless mode

# Path to ChromeDriver
service = Service('C:/Users/renuka/chromedriver.exe')

# Create the WebDriver instance
def create_driver():
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

# Flask route for login and university selection page
@app.route('/login', methods=['POST'])
def login():
    driver = None
    response = {}

    try:
        # Parse input data from the request
        login_value = request.json['login_value']
        password_value = request.json['password_value']
        university_name = request.json.get('university_name')

        # Initialize WebDriver
        driver = create_driver()
        if not driver:
            response = {
                "status": "error",
                "message": "Failed to initialize WebDriver"
            }
            return jsonify(response)

        # Navigate to the login page
        driver.get("https://tsche1.com/verifyTss/reglog/login.php")
        print(f"Current URL: {driver.current_url}")

        # Wait for the login form elements to load
        wait = WebDriverWait(driver, 60)

        try:
            email_input = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
            print("Email input located successfully.")
            email_input.send_keys(login_value)
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error locating email input: {e}"
            }
            return jsonify(response)

        try:
            password_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
            print("Password input located successfully.")
            password_input.send_keys(password_value)
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error locating password input: {e}"
            }
            return jsonify(response)

        try:
            captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, "captcha_code")))
            print("Captcha input located successfully.")
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error locating captcha input: {e}"
            }
            return jsonify(response)

        # Take screenshot of the page
        driver.save_screenshot('full_page_screenshot.png')
        location = captcha_input.location_once_scrolled_into_view
        size = captcha_input.size
        image = Image.open('full_page_screenshot.png')
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        captcha_image = image.crop((left, top, right, bottom))

        # Process CAPTCHA image
        captcha_image = captcha_image.convert('L')
        captcha_image = captcha_image.point(lambda p: p > 128 and 255)
        captcha_image = captcha_image.resize((captcha_image.width * 2, captcha_image.height * 2), Image.LANCZOS)
        captcha_text = pytesseract.image_to_string(captcha_image, config='--oem 3 --psm 6').strip()

        print(f"Captcha Text: {captcha_text}")
        captcha_input.send_keys(captcha_text)

        # Submit the form
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()

        # Wait for page to load after submission
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Welcome')]")))

        # Check if login was successful
        page_source = driver.page_source
        if "Login successful" in page_source:
            response = {
                "status": "success",
                "message": "Login form submitted successfully"
            }
        else:
            response = {
                "status": "error",
                "message": "Login failed or unexpected page load"
            }

    except Exception as e:
        response = {
            "status": "error",
            "message": f"An unexpected error occurred: {e}"
        }

    finally:
        if driver:
            driver.quit()

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, threaded=False)  # Set threaded=False to avoid threading issues
