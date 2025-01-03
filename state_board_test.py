import os
import time
import base64
from flask import Flask, request, jsonify
from selenium import webdriver
from datetime import datetime
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import mysql.connector
import requests

# Setup Chrome options
def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    
    # Set download directory to 'uploads/mhsbe' folder
    download_directory = os.path.join(os.getcwd(), 'uploads', 'mhsbe')  # Using 'uploads/mhsbe'
    os.makedirs(download_directory, exist_ok=True)  # Ensure the directory exists
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options

# Setup the WebDriver (ensure you have the correct path to ChromeDriver)
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

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

def solve_captcha_with_anticaptcha(captcha_image_path, max_attempts=3):
    """Solve CAPTCHA using AntiCaptcha with retries."""
    api_key = '2d6592726aacd80ad4028d234be85561'  # AntiCaptcha API key

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

            time.sleep(5)  # Wait before retrying

        except Exception as e:
            print(f"Error solving CAPTCHA on attempt {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                print("Retrying CAPTCHA...")
            else:
                raise Exception("Max CAPTCHA attempts reached. Please try again later.")

def login_to_website(driver, username, password):
    """Login to the website and handle CAPTCHA."""
    driver.get('https://www.boardmarksheet.maharashtra.gov.in/emarksheet/INDEX.jsp')
    wait = WebDriverWait(driver, 180)

    username_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    print("username input located successfully")
    username_field.send_keys(username)

    password_field = driver.find_element(By.NAME, 'pass')
    print("password input located successfully")
    password_field.send_keys(password)

    captcha_image_element = wait.until(EC.presence_of_element_located((By.ID, "ash")))

    location = captcha_image_element.location_once_scrolled_into_view
    size = captcha_image_element.size

    driver.save_screenshot('uploads/mhsbe/full_page_screenshot.png')  # Save in 'uploads/mhsbe'
    image = Image.open('uploads/mhsbe/full_page_screenshot.png')
    left, top, right, bottom = location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']
    captcha_image = image.crop((left, top, right, bottom))
    captcha_image.save('uploads/mhsbe/captcha_image.png')  # Save in 'uploads/mhsbe'

    captcha_text = solve_captcha_with_anticaptcha('uploads/mhsbe/captcha_image.png')  # Use the folder path here
    captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, "code")))
    print("captcha input located successfully")
    captcha_input.send_keys(captcha_text)

    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Sign In']")))
    print("sign in button clicked successfully")
    sign_in_button.click()
    time.sleep(5)

def navigate_to_verification_page(driver, exam_name):
    """Navigate to the appropriate verification page (SSC or HSC)."""
    wait = WebDriverWait(driver, 40)

    if "10th" in exam_name:
        verify_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'SSCINPUT.jsp')]")))
        verify_link.click()
        print("Navigated to VERIFY SSC/10th MARK SHEET page.")
    elif "12th" in exam_name:
        verify_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'HSCINPUT.jsp')]")))
        verify_link.click()
        print("Navigated to VERIFY HSC/12th MARK SHEET page.")
    else:
        raise ValueError("Invalid exam name provided. Please specify either '10th' or '12th'.")

    time.sleep(5)

def complete_verification(driver, exam_name, exam_year, exam_session, seat_no, obtained_marks):
    """Complete the mark sheet verification process with retry on CAPTCHA failure."""
    wait = WebDriverWait(driver, 40)

    # Select exam year
    year_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'year')))
    for option in year_dropdown.find_elements(By.TAG_NAME, 'option'):
        if option.text == exam_year:
            option.click()
            break

    # Select exam session (FEB, MARCH, MAIN, etc.)
    session_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'session')))
    for option in session_dropdown.find_elements(By.TAG_NAME, 'option'):
        if exam_session.upper() in option.text.upper():  # Match case-insensitively
            option.click()
            break
    else:
        raise ValueError(f"Exam session '{exam_session}' not found in dropdown options.")

    # Enter seat number and marks
    seatno_input = wait.until(EC.visibility_of_element_located((By.NAME, 'seatno')))
    seatno_input.send_keys(seat_no)

    tmark_input = driver.find_element(By.NAME, 'tmark')
    tmark_input.send_keys(obtained_marks)

    # Solve and enter CAPTCHA with retry
    captcha_image_element = wait.until(EC.presence_of_element_located((By.ID, "ash")))

    location = captcha_image_element.location_once_scrolled_into_view
    size = captcha_image_element.size

    driver.save_screenshot('uploads/mhsbe/full_page_screenshot.png')  # Save in 'uploads/mhsbe'
    image = Image.open('uploads/mhsbe/full_page_screenshot.png')
    left, top, right, bottom = location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']
    captcha_image = image.crop((left, top, right, bottom))
    captcha_image.save('uploads/mhsbe/captcha_image.png')  # Save in 'uploads/mhsbe'

    # Attempt solving CAPTCHA multiple times if needed
    captcha_text = solve_captcha_with_anticaptcha('uploads/mhsbe/captcha_image.png')  # Use the folder path here
    code_input = wait.until(EC.visibility_of_element_located((By.NAME, "code")))
    code_input.send_keys(captcha_text)

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "input.form_submit[value='Submit']")
    submit_button.click()
    time.sleep(5)

    # Save the result screenshot
    result_screenshot_path = f"uploads/mhsbe/state_board_result_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"  # Save in 'uploads/mhsbe'
    driver.save_screenshot(result_screenshot_path)

    # Download HSC Marksheet PDF (if available)
    if "12th" in exam_name:
        try:
            download_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@class='form_submit_btn' and @value='Download HSC(12th Exam) Marksheet PDF']")
            ))
            download_button.click()
            print("PDF download initiated.")
            
            # Wait for the file to be downloaded (you can use time.sleep() or a more robust method here)
            time.sleep(5)  # Adjust depending on the download speed

            # Generate filename based on seat_no, exam month, and MARKSHEET
            filename = f"{seat_no[:7]}{exam_year}{exam_session.upper()}MARKSHEET.pdf"  # Format: M219366MARCHMARKSHEET.pdf

            # Move the downloaded PDF to the correct file name in the 'uploads/mhsbe' directory
            download_path = os.path.join(os.getcwd(), 'uploads', 'mhsbe', filename)
            if os.path.exists(download_path):
                print(f"PDF downloaded and saved to {download_path}")
            else:
                print(f"Failed to download PDF to {download_path}")

        except Exception as e:
            print(f"Error downloading PDF: {e}")

    if "10th" in exam_name:
        try:
            download_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@class='form_submit_btn' and @value='Download SSC(10th Exam) Marksheet PDF']")
            ))
            download_button.click()
            print("PDF download initiated.")
            
            # Wait for the file to be downloaded (you can use time.sleep() or a more robust method here)
            time.sleep(5)  # Adjust depending on the download speed

            # Generate filename based on seat_no, exam month, and MARKSHEET
            filename = f"{seat_no[:7]}{exam_year}{exam_session.upper()}MARKSHEET.pdf"  # Format: M219366MARCHMARKSHEET.pdf

            # Move the downloaded PDF to the correct file name in the 'uploads/mhsbe' directory
            download_path = os.path.join(os.getcwd(), 'uploads', 'mhsbe', filename)
            if os.path.exists(download_path):
                print(f"PDF downloaded and saved to {download_path}")
            else:
                print(f"Failed to download PDF to {download_path}")

        except Exception as e:
            print(f"Error downloading PDF: {e}")

    return result_screenshot_path


@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    exam_name = data.get('exam_name')
    exam_year = data.get('exam_year')
    exam_session = data.get('exam_session')
    seat_no = data.get('seat_no')
    obtained_marks = data.get('obtained_marks')

    if not all([username, password, exam_name, exam_year, exam_session, seat_no, obtained_marks]):
        return jsonify({"error": "All inputs are required"}), 400

    driver = webdriver.Chrome(service=service, options=setup_chrome_options())
    try:
        login_to_website(driver, username, password)
        navigate_to_verification_page(driver, exam_name)
        result_screenshot = complete_verification(driver, exam_name, exam_year, exam_session, seat_no, obtained_marks)
        save_filename_to_db(username, password, result_screenshot)
        return jsonify({"message": "Verification completed successfully!", "screenshot": result_screenshot})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
