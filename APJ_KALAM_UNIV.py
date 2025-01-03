from flask import Flask, request, jsonify
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Setup the web driver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

app = Flask(__name__)

def save_filename_to_db(username, password, filename):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='education_schema'
        )
        cursor = connection.cursor()
        insert_query = 'INSERT INTO login_details (login_value, password_value, filename) VALUES (%s, %s, %s)'
        cursor.execute(insert_query, (username, password, filename))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_page_screenshot(driver, filename):
    driver.save_screenshot(filename)
    print(f"Screenshot saved as: {filename}")

def open_website(driver, registration_number, date_of_birth):
    try:
        driver.get('https://verification.ktu.edu.in/verificationPortal/')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'formRegisterNumber')))

        # Enter registration number
        registration_number_input = driver.find_element(By.ID, 'formRegisterNumber')
        registration_number_input.send_keys(registration_number)

        # Enter date of birth
        date_of_birth_input = driver.find_element(By.ID, 'formDob')
        date_of_birth_input.send_keys(date_of_birth)

        # Click the search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.blue-btn.btn-primary"))
        )
        search_button.click()

        # Check for reCAPTCHA error
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.alert.alert-danger'))
            )
            error_message = driver.find_element(By.CSS_SELECTOR, 'div.alert.alert-danger').text
            if "Error occurred while validating recaptcha" in error_message:
                return {"error": "Service Unavailable", "captcha_error": True}
        except Exception:
            pass

        # Wait for the result container to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h3.text-white'))
        )

        # Save the page screenshot
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        screenshot_filename = f"apj_kalam_univ_result_{timestamp}.png"
        save_page_screenshot(driver, screenshot_filename)

        # Save filename to the database
        save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

        return {"screenshot": screenshot_filename}
    except Exception as e:
        print(f"Error during form submission: {str(e)}")
        driver.quit()
        raise

@app.route('/generate_result', methods=['POST'])
def generate_result():
    data = request.get_json()
    registration_number = data.get('registration_number')
    date_of_birth = data.get('date_of_birth')

    if not registration_number or not date_of_birth:
        return jsonify({"error": "Hall ticket number and date of birth are required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result = open_website(driver, registration_number, date_of_birth)
        if result.get("captcha_error"):
            return jsonify({"error": "Service Unavailable: CAPTCHA validation failed"}), 503
        return jsonify({"message": "Result generated successfully", "screenshot": result.get("screenshot")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
