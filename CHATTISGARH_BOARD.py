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
# chrome_options.add_argument('--headless')

# Setup the web driver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# Set download directory to 'uploads/bieandhra' folder
download_directory = os.path.join(os.getcwd(), 'uploads')
os.makedirs(download_directory, exist_ok=True)
prefs = {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Setup the Flask app
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
        insert_query = '''
            INSERT INTO login_details (login_value, password_value, filename)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(insert_query, (username, password, filename))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def open_website(driver, exam_course, exam_year, roll_number):
    try:
        wait = WebDriverWait(driver, 30)
        driver.get('https://abhilekh.cgbse.nic.in/counter/')
        print("Website loaded successfully")

        # Select exam course dropdown
        exam_course_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ctl00$ContentPlaceHolder1$ddlcourse')))
        print("Exam course dropdown visible and clickable")

        for option in exam_course_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == exam_course:
                option.click()
                print(f"Selected exam course: {exam_course}")
                break
        else:
            raise ValueError("Exam course not found in dropdown options!")
        
        # Add delay or wait for changes to take effect
        time.sleep(2)  # Adding a wait before the next interaction to avoid stale element reference

        # Re-find the exam year dropdown after selecting the course
        exam_year_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ctl00$ContentPlaceHolder1$ddlYear')))
        print("Exam year dropdown visible and clickable")

        for option in exam_year_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == exam_year:
                option.click()
                print(f"Selected exam year: {exam_year}")
                break
        else:
            raise ValueError("Exam year not found in dropdown options!")

        # Re-find and fill the roll number
        roll_number_input = wait.until(EC.visibility_of_element_located((By.NAME, 'ctl00$ContentPlaceHolder1$txtRollNo')))
        roll_number_input.send_keys(roll_number)
        print(f"Entered roll number: {roll_number}")

        time.sleep(30)  # Wait for CAPTCHA to appear

        # Extract CAPTCHA text from the span element
        captcha_text_element = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_imgCaptcha')))
        print("CAPTCHA text element found.")

        captcha_text = captcha_text_element.text.strip()
        print(f"Extracted CAPTCHA text: {captcha_text}")

        if not captcha_text:
            raise ValueError("CAPTCHA text is not visible or failed to extract.")

        # Enter the CAPTCHA
        captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, 'ctl00$ContentPlaceHolder1$txtCaptcha')))
        captcha_input.clear()  # Clear any existing text
        captcha_input.send_keys(captcha_text)
        print("Entered CAPTCHA text into the input field")

        # Wait a moment to make sure CAPTCHA input is accepted
        time.sleep(2)

        # Re-locate the search button and click it
        search_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_btnSearch')))
        print("Search button located and clickable")

        # Use JavaScript to click the button directly, bypassing the onclick handler
        driver.execute_script("arguments[0].click();", search_button)
        print("Search button clicked using JavaScript")

        time.sleep(30)
    
        # heading_element = wait.until(
        #     EC.presence_of_element_located((By.XPATH, "//center//h2[text()='HIGHER SECONDARY']"))
        # )
        # print("Heading found")

        # if heading_element:
        
        result_screenshot_path = f"uploads/chattisgarh_board_result_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        driver.save_screenshot(result_screenshot_path)
        print(f"Screenshot saved at: {result_screenshot_path}")

        # Save the filename to the database
        save_filename_to_db('finance@mistitservices.com', '1234mkM#', result_screenshot_path)

        return {"filename": result_screenshot_path, "status": True}
        
        # else:
        #     return {"message":"No data found!", "status":False}

    except Exception as e:
        print(f"Error during website interaction: {e}")
        raise


@app.route('/generate_result', methods=['POST'])
def generate_result_data():
    data = request.get_json()
    exam_course = data.get('exam_course')
    exam_year = data.get('exam_year')
    roll_number = data.get('roll_number')
    if not all([exam_course, exam_year, roll_number]):
        return jsonify({"error": "All inputs are required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    captcha_failed = False
    try:
        result_data = open_website(driver, exam_course, exam_year, roll_number)
        print(f"Result Data: {result_data}")  # Add this line to debug
        
        # Ensure result_data is a dictionary with 'filename'
        filename = result_data.get('filename')
        if filename:
            return jsonify({
                "status": True,
                "message": "Verification completed successfully!",
                "filename": filename
            })
        else:
            raise ValueError("Screenshot filename is not returned.")
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
        
        return jsonify(response_message), 500
    finally:
        driver.quit()


if __name__ == '__main__':
    app.run(debug=True)
