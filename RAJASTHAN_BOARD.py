
from flask import Flask, request, jsonify
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import mysql.connector
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
        print("Filename successfully saved to database.")
    except mysql.connector.Error as err:
        print(f"Error while saving filename to database: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def open_website(driver, exam_course, exam_year, roll_number):
    try:
        wait = WebDriverWait(driver, 30)
        driver.get('http://117.239.28.178:8081/OLDRESULT/view_TR.asp')

        # Select exam year
        exam_year_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'cmb_year')))
        for option in exam_year_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == exam_year:
                option.click()
                break
        else:
            raise ValueError("Exam year not found in dropdown options!")

        # Select exam course
        exam_course_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'cmb_exam')))
        for option in exam_course_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == exam_course:
                option.click()
                break
        else:
            raise ValueError("Exam course not found in dropdown options!")

        # Enter hall ticket number
        roll_number_input = wait.until(EC.visibility_of_element_located((By.NAME, 'txt_roll')))
        roll_number_input.send_keys(roll_number)

        # Locate and click the submit button
        submit_button = wait.until(EC.element_to_be_clickable((By.NAME, 'b1')))
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait for the "BOARD OF SECONDARY EDUCATION, RAJASTHAN" heading to appear
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//td[font[contains(text(), 'BOARD OF SECONDARY EDUCATION, RAJASTHAN')]]")))
            # Take a screenshot of the page if heading is found
            result_screenshot_path = f"uploads/rajasthan_board_result_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
            driver.save_screenshot(result_screenshot_path)
            print(f"Screenshot saved at {result_screenshot_path}")

            return {
                "screenshot_path": result_screenshot_path
            }

        except TimeoutException:
            # If the heading is not found, return a message
            print("No data found - 'BOARD OF SECONDARY EDUCATION, RAJASTHAN' heading not found.")
            return {
                "error": "No data found"
            }

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
        return jsonify({"error": "All inputs are required"})

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result_data = open_website(driver, exam_course, exam_year, roll_number)

        if 'screenshot_path' in result_data:
            save_filename_to_db(
                'finance@mistitservices.com',
                '1234mkM#',
                result_data.get('screenshot_path')  # Pass the screenshot path as filename
            )

            return jsonify({
                "status": True,
                "message": "Verification completed successfully!",
                "filename": result_data['screenshot_path']  # Include the screenshot filename here

            })
        else:
            return jsonify({
                "status": False,
                "message": result_data.get('error', 'Unknown error')
            })
    except Exception as e:
        error_message = str(e)
        print(f"Error during result generation: {error_message}")

        response_message = {
            "message": "An issue occurred while processing your request.",
            "status": False
        }

        return jsonify(response_message), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
