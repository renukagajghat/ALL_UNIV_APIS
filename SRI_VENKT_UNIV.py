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
chrome_options.add_argument('--headless')

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

def open_website(driver, hall_ticket_number):
    try:
        driver.get('https://www.results.manabadi.co.in/sri-venkateswara-university-BA-BCOM-BSC-BCA-BBA-IV-SEM-April-2019-exam-results-29062019.htm')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'htno')))

        # Enter hall ticket number
        hall_ticket_input = driver.find_element(By.NAME, 'htno')
        hall_ticket_input.send_keys(hall_ticket_number)

        # Click the submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'btnsubmit'))
        )
        submit_button.click()

        WebDriverWait(driver, 80).until(EC.element_to_be_clickable((By.ID, 'btnsubmit')))


        # Save the page screenshot
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        screenshot_filename = f"sri_venkt_univ_result_{timestamp}.png"
        save_page_screenshot(driver, screenshot_filename)

        # Save filename to the database
        save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

        return screenshot_filename
    except Exception as e:
        print(f"Error during form submission: {str(e)}")
        driver.quit()
        raise

@app.route('/generate_result', methods=['POST'])
def generate_result():
    data = request.get_json()
    hall_ticket_number = data.get('hall_ticket_number')

    if not hall_ticket_number:
        return jsonify({"error": "Hall ticket number is required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        screenshot_filename = open_website(driver, hall_ticket_number)
        return jsonify({"message": "Result generated successfully", "screenshot": screenshot_filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
