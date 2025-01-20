from flask import Flask, request, jsonify
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import requests
import base64
import time
import os

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--headless')

# Setup the web driver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# Set download directory to 'uploads/bieandhra' folder
download_directory = os.path.join(os.getcwd(), 'uploads', 'bieandhra')
os.makedirs(download_directory, exist_ok=True)
prefs = {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Setup the Flask app
app = Flask(__name__)

def save_filename_to_db(username, password, filename, name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='education_schema'
        )
        cursor = connection.cursor()
        insert_query = '''
            INSERT INTO login_details (login_value, password_value, filename, name)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(insert_query, (username, password, filename, name))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def solve_captcha_with_anticaptcha(captcha_image_path, max_attempts=3):
    api_key = '09e4c1ee0134815fde031aa2fd2a2063'
    for attempt in range(max_attempts):
        try:
            with open(captcha_image_path, 'rb') as captcha_file:
                captcha_image_data = captcha_file.read()
                captcha_image_base64 = base64.b64encode(captcha_image_data).decode('utf-8')

            response = requests.post(
                'https://api.anti-captcha.com/createTask',
                json={
                    "clientKey": api_key,
                    "task": {
                        "type": "ImageToTextTask",
                        "body": captcha_image_base64
                    }
                }
            )

            response_json = response.json()
            if 'taskId' not in response_json:
                raise ValueError("Failed to create CAPTCHA task.")

            task_id = response_json['taskId']
            while True:
                result_response = requests.post(
                    'https://api.anti-captcha.com/getTaskResult',
                    json={
                        "clientKey": api_key,
                        "taskId": task_id
                    }
                )
                result_json = result_response.json()
                if result_json['status'] == 'ready':
                    return result_json['solution']['text']
                time.sleep(5)
        except Exception as e:
            print(f"Error solving CAPTCHA on attempt {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                print("Retrying CAPTCHA...")
            else:
                raise Exception("Max CAPTCHA attempts reached. Please try again later.")

def open_website(driver, hall_ticket_number, date_of_birth, email_id):
    try:
        wait = WebDriverWait(driver, 10)
        driver.get('https://bie.ap.gov.in/DuplicateTripilateCerti')

        # Select exam type
        exam_type_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'type')))
        for option in exam_type_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == 'Duplicate Pass Certificate':
                option.click()
                break
        else:
            raise ValueError("Exam type not found in dropdown options!")

        # Enter hall ticket number
        hall_ticket_number_input = wait.until(EC.visibility_of_element_located((By.NAME, 'rollno')))
        hall_ticket_number_input.send_keys(hall_ticket_number)

        # Enter date of birth
        date_of_birth_input = wait.until(EC.visibility_of_element_located((By.NAME, 'date_of_birth')))
        date_of_birth_input.send_keys(date_of_birth)

        # Enter email ID
        email_id_input = wait.until(EC.visibility_of_element_located((By.NAME, 'email_id')))
        email_id_input.send_keys(email_id)

        # Locate CAPTCHA image and extract base64 data
        captcha_image_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'captcha-image')))
        captcha_base64 = captcha_image_element.get_attribute('src').split(",")[1]  # Extract the base64 part

        # Decode and save the CAPTCHA image
        captcha_image_path = 'uploads/bieandhra/captcha_image.png'
        with open(captcha_image_path, 'wb') as captcha_file:
            captcha_file.write(base64.b64decode(captcha_base64))

        # Solve CAPTCHA with retries
        captcha_text = solve_captcha_with_anticaptcha(captcha_image_path)

        # Ensure CAPTCHA field is visible before entering text
        captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, 'enter_captcha')))
        captcha_input.clear()  # Clear any existing text
        captcha_input.send_keys(captcha_text)

        # Wait a moment to make sure CAPTCHA input is accepted
        time.sleep(2)

        # Locate and click the Search button (using explicit wait and JavaScript click)
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(@class, "btn-success")]')))
        
        # Scroll to the button to make sure it's in view
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)

        # Use JavaScript to click the button if the normal click doesn't work
        driver.execute_script("arguments[0].click();", search_button)

        # Wait for the "Student Details" heading to appear
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[text()='Student Details']")))

        # Take a screenshot of the student details page
        result_screenshot_path = f"uploads/bieandhra/student_details_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        driver.save_screenshot(result_screenshot_path)

        # Scroll to the bottom of the page to ensure everything is loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give time for the page to load if needed

        # Extract name correctly from the 'value' attribute of the input element
        name_element = driver.find_element(By.NAME, 'candidate_name')
        name = name_element.get_attribute('value')  # Get value, not text

    except Exception as e:
        print(f"Error during website interaction: {e}")
        raise

    return {
        "screenshot_path": result_screenshot_path,
        "name": name
    }

@app.route('/generate_result', methods=['POST'])
def generate_result_data():
    data = request.get_json()
    hall_ticket_number = data.get('hall_ticket_number')
    date_of_birth = data.get('date_of_birth')
    email_id = data.get('email_id')
    if not all([hall_ticket_number, date_of_birth, email_id]):
        return jsonify({"error": "All inputs are required"})

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result_data = open_website(driver, hall_ticket_number, date_of_birth, email_id)
        save_filename_to_db(
            'finance@mistitservices.com',
            '1234mkM#',
            result_data.get('screenshot_path'),  # Pass the screenshot path as filename
            result_data.get('name')
        )

        return jsonify({
            "status":True,
            "message": "Verification completed successfully!",
            "name": result_data['name']
        })
    except Exception as e:
        error_message = str(e)
        if "CAPTCHA" in error_message.upper():  # Detect if the error is related to CAPTCHA
            captcha_failed = True

        # Log the error for debugging
        print(f"Error: {e}")
        
        # Provide a user-friendly error message
        response_message = {
            "message": "An issue occurred while processing your request.",
            "status": False
        }

        if captcha_failed:
            response_message["message"] += " CAPTCHA is not working, so this code failed. Please try again later."
        
        return jsonify(response_message), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
