from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import datetime
import mysql.connector

# Setup the chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-web-security')
# chrome_options.add_argument('--headless')

# Setup the webdriver
service = Service('C:/Users/renuka/chromedriver.exe')

# Initialize the flask app
app = Flask(__name__)

# Create database connection
def save_filename_to_db(username, password, filename):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="education_schema"
        )
        cursor = connection.cursor()
        insert_query = "insert into login_details(login_value, password_value, filename) values (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, filename))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error:{err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def save_page_screenshot(driver, filename):
    driver.save_screenshot(filename)
    print(f"Screenshot saved as:{filename}")


def open_website(driver, dvf_number):
    try:
        driver.get('https://durslt.du.ac.in/DU_Online_Certificate/Digi_Auth.aspx')

        # Enter DVF number
        dvf_no_input = driver.find_element(By.NAME, 'txtdbno')
        dvf_no_input.send_keys(dvf_number)

        # Locate the search button
        search_button_element = driver.find_element(By.ID, 'btnsearch')

        # Wait for the search button to be clickable
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(search_button_element)
        )
        # Click the search button
        search_button.click()

        try:
            # Wait for the document details table to load
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.ID, 'pnl_view'))  # Wait for the content div
            )

            time.sleep(5)  # Wait some additional time to allow content to load fully

            # Check if the document section contains data
            document_details = driver.find_element(By.ID, 'pnl_view')

            # If the document details section has content, take a screenshot
            if document_details:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                screenshot_filename = f"uploads/delhi_univ_details_{timestamp}.png"
                save_page_screenshot(driver, screenshot_filename)

                # Save the filename to the database
                save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

                return {"filename": screenshot_filename, "status": True}
            else:
                return {"message": "No data found", "status": False}

        except Exception as e:
            print(f"Error while checking document details: {str(e)}")
            return {"message": "No data found", "status": False}

    except Exception as e:
        print(f"Error during form submission: {str(e)}")
        raise e


@app.route('/generate_result', methods=['POST'])
def generate_result():
    data = request.get_json()
    dvf_number = data.get('dvf_number')

    if not dvf_number:
        return jsonify({"error": "dvf number required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result = open_website(driver, dvf_number)
        if result['status']:
            return jsonify({"message": "Result generated successfully", "status": True, "filename": result['filename']})
        else:
            return jsonify({"message": "No data found", "status": False}), 404

    except Exception as e:
        print(f"Error: {e}")
        response_message = {
            "message": "An issue occurred while processing your request.",
            "status": False
        }
        return jsonify(response_message), 500
    finally:
        driver.quit()


if __name__ == '__main__':
    app.run(debug=True)
