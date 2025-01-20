# from flask import Flask, request, jsonify
# from PIL import Image
# from selenium import webdriver
# from datetime import datetime
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import mysql.connector
# import requests
# import base64
# import time

# # Setup Chrome options
# chrome_options = Options()
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--window-size=1920,1080')
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--disable-blink-features=AutomationControlled')
# chrome_options.add_argument('--disable-web-security')
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option('useAutomationExtension', False)
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# # chrome_options.add_argument('--headless')

# # Setup the web driver
# service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# app = Flask(__name__)

# def save_result_to_db(username, password, filename, name, percentage):
#     """Save login details, name, percentage, and filename into the database."""
#     try:
#         # Connect to the database
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="education_schema"
#         )
#         cursor = connection.cursor()

#         # Insert data into the table
#         insert_query = """
#         INSERT INTO login_details (login_value, password_value, filename, name, percentage)
#         VALUES (%s, %s, %s, %s, %s)
#         """
#         cursor.execute(insert_query, (username, password, filename, name, percentage))

#         # Commit the transaction
#         connection.commit()
#         print(f"Data saved successfully with name: {name}, percentage: {percentage}")

#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()


# def solve_captcha_with_anticaptcha(captcha_image_path, max_attempts=3):
#     """Solve CAPTCHA using AntiCaptcha with retries."""
#     api_key = '8e44196b1eb8d11cada78cee897f4b76'  # AntiCaptcha API key

#     for attempt in range(max_attempts):    
#         try:
#             with open(captcha_image_path, 'rb') as captcha_file:
#                 captcha_image_data = captcha_file.read()
#                 captcha_image_base64 = base64.b64encode(captcha_image_data).decode('utf-8')

#                 response = requests.post(
#                     'https://api.anti-captcha.com/createTask',
#                     json={
#                         "clientKey": api_key,
#                         "task": {
#                             "type": "ImageToTextTask",
#                             "body": captcha_image_base64
#                         }
#                     }
#                 )
#                 response_json = response.json()
#                 task_id = response_json['taskId']

#                 while True:
#                     result_response = requests.post(
#                         'https://api.anti-captcha.com/getTaskResult',
#                         json={
#                             "clientKey": api_key,
#                             "taskId": task_id
#                         }
#                     )
#                     result_json = result_response.json()

#                     if result_json['status'] == 'ready':
#                         return result_json['solution']['text']
                    
#                     time.sleep(5)  # Wait before retrying

#         except Exception as e:
#             print(f"Error solving CAPTCHA on attempt {attempt + 1}: {e}")
#             if attempt < max_attempts - 1:
#                 print("Retrying CAPTCHA...")
#             else:
#                 raise Exception("Max CAPTCHA attempts reached. Please try again later.")    


# def save_page_screenshot(driver, filename):
#     driver.save_screenshot(filename)
#     print(f"Screenshot saved as: {filename}")


# def open_website(driver, enrollment_number, password):
#     try:
#         driver.get('https://www.students.gtu.ac.in/Default.aspx')
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtEnrollNo')))

#         # Enter enrollment number
#         enrollment_number_input = driver.find_element(By.ID, 'txtEnrollNo')
#         enrollment_number_input.send_keys(enrollment_number)

#         # Enter password
#         password_input = driver.find_element(By.ID, 'txtpassword')
#         password_input.send_keys(password)

#         wait = WebDriverWait(driver, 10)

#         captcha_image_element = wait.until(EC.presence_of_element_located((By.ID, "imgCaptcha")))

#         location = captcha_image_element.location_once_scrolled_into_view
#         size = captcha_image_element.size

#         driver.save_screenshot('full_page_screenshot.png')
#         image = Image.open('full_page_screenshot.png')
#         left, top, right, bottom = location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']
#         captcha_image = image.crop((left, top, right, bottom))
#         captcha_image.save('captcha_image.png')

#         captcha_text = solve_captcha_with_anticaptcha('captcha_image.png')
#         captcha_input = driver.find_element(By.NAME, "CodeNumberTextBox")
#         captcha_input.send_keys(captcha_text)

#         # Click the submit button
#         submit_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, 'btnSubmit'))
#         )
#         submit_button.click()

#         # Wait for the result to load
#         WebDriverWait(driver, 200).until(
#             EC.presence_of_element_located((By.ID, 'lblName'))  # Wait until the name element is present
#         )

#         # Extract name and percentage
#         name_element = driver.find_element(By.ID, 'lblName')
#         name = name_element.text

#         percentage_element = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.XPATH, '//table[@id="grdvLastExm"]//tr[2]/td[last()]'))
#         )
#         percentage = percentage_element.text

#         # Save the page screenshot
#         timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
#         screenshot_filename = f"guj_tech_univ_result_{timestamp}.png"
#         save_page_screenshot(driver, screenshot_filename)

#         # Save data to the database
#         save_result_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename, name, percentage)

#         return {"screenshot": screenshot_filename, "name": name, "percentage": percentage}
#     except Exception as e:
#         print(f"Error during form submission: {str(e)}")
#         driver.quit()
#         raise


# @app.route('/generate_result', methods=['POST'])
# def generate_result():
#     data = request.get_json()
#     enrollment_number = data.get('enrollment_number')
#     password = data.get('password')

#     if not enrollment_number or not password:
#         return jsonify({"error": "Hall ticket number and date of birth are required"}), 400

#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     try:
#         result_data = open_website(driver, enrollment_number, password)
#         return jsonify({
#             "message": "Result generated successfully",
#             "screenshot": result_data["screenshot"],
#             "name": result_data["name"],
#             "percentage": result_data["percentage"]
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         driver.quit()


# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
from PIL import Image
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import requests
import base64
import time

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
# chrome_options.add_argument('--headless')

# Setup the web driver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

app = Flask(__name__)

def save_result_to_db(username, password, filename, name, percentage):
    """Save login details, name, percentage, and filename into the database."""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="education_schema"
        )
        cursor = connection.cursor()

        # Insert data into the table
        insert_query = """
        INSERT INTO login_details (login_value, password_value, filename, name, percentage)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (username, password, filename, name, percentage))

        # Commit the transaction
        connection.commit()
        print(f"Data saved successfully with name: {name}, percentage: {percentage}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def solve_captcha_with_anticaptcha(captcha_image_path, max_attempts=3):
    """Solve CAPTCHA using AntiCaptcha with retries."""
    api_key = '09e4c1ee0134815fde031aa2fd2a2063'  # AntiCaptcha API key

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


def save_page_screenshot(driver, filename):
    driver.save_screenshot(filename)
    print(f"Screenshot saved as: {filename}")


def open_website(driver, enrollment_number, password):
    try:
        driver.get('https://www.students.gtu.ac.in/Default.aspx')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtEnrollNo')))

        # Enter enrollment number
        enrollment_number_input = driver.find_element(By.ID, 'txtEnrollNo')
        enrollment_number_input.send_keys(enrollment_number)

        # Enter password
        password_input = driver.find_element(By.ID, 'txtpassword')
        password_input.send_keys(password)

        wait = WebDriverWait(driver, 10)

        captcha_image_element = wait.until(EC.presence_of_element_located((By.ID, "imgCaptcha")))

        location = captcha_image_element.location_once_scrolled_into_view
        size = captcha_image_element.size

        driver.save_screenshot('full_page_screenshot.png')
        image = Image.open('full_page_screenshot.png')
        left, top, right, bottom = location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']
        captcha_image = image.crop((left, top, right, bottom))
        captcha_image.save('captcha_image.png')

        captcha_text = solve_captcha_with_anticaptcha('captcha_image.png')
        captcha_input = driver.find_element(By.NAME, "CodeNumberTextBox")
        captcha_input.send_keys(captcha_text)

        # Click the submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'btnSubmit'))
        )
        submit_button.click()

        # Wait for the result to load
        WebDriverWait(driver, 200).until(
            EC.presence_of_element_located((By.ID, 'lblName'))  # Wait until the name element is present
        )

        # Extract name and percentage
        name_element = driver.find_element(By.ID, 'lblName')
        name = name_element.text

        percentage_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[@id="grdvLastExm"]//tr[2]/td[last()]'))
        )
        percentage = percentage_element.text

        # Save the page screenshot
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        screenshot_filename = f"guj_tech_univ_result_{timestamp}.png"
        save_page_screenshot(driver, screenshot_filename)

        # Save data to the database
        save_result_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename, name, percentage)

        return {"screenshot": screenshot_filename, "name": name, "percentage": percentage}
    except Exception as e:
        print(f"Error during form submission: {str(e)}")
        driver.quit()
        raise


@app.route('/generate_result', methods=['POST'])
def generate_result():
    data = request.get_json()
    enrollment_number = data.get('enrollment_number')
    password = data.get('password')

    if not enrollment_number or not password:
        return jsonify({"error": "Hall ticket number and date of birth are required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result_data = open_website(driver, enrollment_number, password)
        return jsonify({
            "status":True,
            "message": "Result generated successfully",
            "screenshot": result_data["screenshot"],
            "name": result_data["name"],
            "percentage": result_data["percentage"]
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
