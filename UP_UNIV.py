from flask import Flask, request, jsonify
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import time
import os
import base64
import requests
from PIL import Image
import pytesseract

# Chrome options setup
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--start-maximized')
# chrome_options.add_argument('--headless')  # Uncomment for headless mode

# Setup WebDriver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

app = Flask(__name__)

# Upload directory setup
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Save filename to the database
def save_filename_to_db(username, password, filename):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="education_schema"
        )
        cursor = connection.cursor()

        insert_query = """INSERT INTO login_details (login_value, password_value, filename) VALUES (%s, %s, %s)"""
        cursor.execute(insert_query, (username, password, filename))

        connection.commit()
        print(f"Data saved successfully with file {filename}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Save screenshot of the page
def save_page_screenshot(driver, filename):
    driver.save_screenshot(filename)
    print(f"Screenshot saved as {filename}")

# Process CAPTCHA image to extract text
def solve_captcha_with_anticaptcha(captcha_image_path, max_attempts = 3):
    """solve captcha using anticaptcha with retries"""
    api_key = '8e44196b1eb8d11cada78cee897f4b76'  # AntiCaptcha API key

    for attempt in range(max_attempts):    
        try:
            with open(captcha_image_path, 'rb') as captcha_file:
                captcha_image_data = captcha_file.read()
                captcha_image_base64 = base64.b64encode(captcha_image_data).decode('utf-8')

                response = requests.post(
                    'https://api.anti-captcha.com/createTask',
                    json={
                        "clientKey":api_key,
                        "task":{
                            "type":"ImageToTextTask",
                            "body":captcha_image_base64

                        }

                    }

                )
            response_json = response.json()
            task_id = response_json['taskId']

            while True:
                result_response = requests.post(
                    'https://api.anti-captcha.com/getTaskResult',
                    json={
                        "clientKey":api_key,
                        "taskId":task_id
                    }

                )
                result_json = result_response.json()

                if result_json['status'] == 'ready':
                    return result_json['solution']['text']
                
            time.sleep(5) #wait before retrying

        except Exception as e:
            print(f"Error solving CAPTCHA on attempt{attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                print("Retrying CAPTCHA...")
            else:
                raise Exception("Max CAPTCHA attempts reached. Pleased try again later.")    





@app.route('/generate_result', methods=['POST'])
def generate_result():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        exam_name = data.get('exam_name')  # Dynamic input for exam name
        year = data.get('year')  # Dynamic input for year
        roll_number = data.get('roll_number')  # Roll number passed via Postman

        # Start WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the website
        driver.get('https://ubse.upmsp.edu.in/')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print("Website loaded successfully")

        # Scroll and find the correct exam link as before
        target_link = None
        last_height = driver.execute_script("return document.body.scrollHeight")
        found = False

        while not found:
            rows = driver.find_elements(By.XPATH, "//tr")

            for row in rows:
                try:
                    exam_name_element = row.find_element(By.XPATH, ".//td[2]")
                    year_element = row.find_element(By.XPATH, ".//td[3]/b")
                    link_element = row.find_element(By.XPATH, ".//td[4]/a")

                    extracted_exam_name = exam_name_element.text.strip()
                    extracted_year = year_element.text.strip()

                    if exam_name in extracted_exam_name and str(year) in extracted_year:
                        target_link = link_element.get_attribute('href')
                        print(f"Found target link: {target_link}")
                        found = True
                        break
                except Exception as e:
                    continue

            if found:
                break

            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached the bottom of the page, but no matching data found.")
                break
            last_height = new_height

        if not target_link:
            return jsonify({"error": "Exam name or year range not found"}), 404

        driver.get(target_link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print("Result page loaded successfully")

        year_input = driver.find_element(By.XPATH, '//*[@id="ctl00_cphBody_ddl_ExamYear"]')  # Replace with correct XPath
        print("year input located successfully")       
        year_input.send_keys(str(year))

        # Fill the roll number and year inputs
        roll_number_input = driver.find_element(By.XPATH, '//*[@id="ctl00_cphBody_txt_RollNumber"]')  # Replace with correct XPath
        print("roll_number input located successfully")
        roll_number_input.send_keys(roll_number)
        
        wait = WebDriverWait(driver, 10)

        captcha_image_element = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphBody_IMGCaptcha")))

        location = captcha_image_element.location_once_scrolled_into_view
        size = captcha_image_element.size

        driver.save_screenshot('full_page_screenshot.png')
        image = Image.open('full_page_screenshot.png')
        left, top, right, bottom = location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']
        captcha_image = image.crop((left, top, right, bottom))
        captcha_image.save('captcha_image.png')

        captcha_text = solve_captcha_with_anticaptcha('captcha_image.png')
        captcha_input = driver.find_element(By.XPATH, '//*[@id="ctl00_cphBody_TxtCAPTCHA"]')  # Replace with correct XPath
        print("captcha input located successfully")
        captcha_input.send_keys(captcha_text)


        # Click "View Result" button
        view_result_button = driver.find_element(By.XPATH, '//*[@id="ctl00_cphBody_btnSubmit"]')  # Replace with correct XPath
        view_result_button.click()

        # Save the result screenshot
        screenshot_filename = f"uttarpradesh_univ_result_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        driver.save_screenshot(screenshot_filename)

        # Save filename into the database
        save_filename_to_db(username, password, screenshot_filename)

        driver.quit()

        return jsonify({"message": "Result fetched and screenshot saved successfully", "filename": screenshot_filename})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)