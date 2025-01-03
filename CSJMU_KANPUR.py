from flask import Flask, request, jsonify
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
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
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Setup the web driver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# Set download directory to 'uploads/bieandhra' folder
download_directory = os.path.join(os.getcwd(), 'uploads', 'csjmu')
os.makedirs(download_directory, exist_ok=True)
prefs = {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

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

def open_website(driver, exam_session, course_type, exam_type, course_name, semister, roll_number):
    try:
        wait = WebDriverWait(driver, 40)

        driver.get('https://results.csjmu.ac.in/webpages/resultviewlogin.aspx')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h5[@class='card-title' and text() = 'CSJMU Results']")))

        # Select exam session
        exam_session_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlSession')))

        # Convert the exam session to the correct value based on the year
        start_year = int(exam_session) - 1  # Subtract 1 to get the start year of the session
        target_value = str(start_year + 1)  # This should now be "2019-20" for "2020" exam session

        # Match dropdown option by value
        matched = False
        for option in exam_session_dropdown.find_elements(By.TAG_NAME, 'option'):
            option_value = option.get_attribute("value")
            if option_value == target_value:
                option.click()
                matched = True
                break

        if not matched:
            raise ValueError(f"Exam session '{exam_session}' not found in dropdown options. Looked for '{target_value}'.")
        

        # Select the course type
        course_type_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlCourseType')))
        for option in course_type_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip().upper() == course_type.upper():
                option.click()
                break
        else:
            raise ValueError(f"Course type '{course_type}' not found in dropdown options.")
        
        #Select the exam type
        exam_type_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlExamType')))
        for option in exam_type_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip().upper() == exam_type.upper():
                option.click()
                break
        else:
            raise ValueError(f"Exam type '{exam_type}' not found in dropdown options.")    

        #select the course name
        course_name_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlCourse')))
        for option in course_name_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip().upper() == course_name.upper():
                option.click()
                break
        else:
            raise ValueError(f"Course Name '{course_name}' not found in dropdown options.")    

        #select semister dropdown
        semister_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlYearSem')))
        for option in semister_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip().upper() == semister.upper():
                option.click()
                break
        else:
            raise ValueError(f"Semister '{semister}' not found in dropdown options.")

        # Enter roll number
        roll_number_input = wait.until(EC.visibility_of_element_located((By.NAME, 'txtRollNo')))
        roll_number_input.send_keys(roll_number)   

        # Click the search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnSearch"))
        )
        search_button.click()
 
        wait = WebDriverWait(driver, 40)

        # Take a screenshot of the student details page
        result_screenshot_path = f"uploads/csjmu/csjmu_kanpur_univ_result_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        driver.save_screenshot(result_screenshot_path)

        # Save filename to the database
        save_filename_to_db('finance@mistitservices.com', '1234mkM#', result_screenshot_path)

        return {"screenshot": result_screenshot_path}
    except Exception as e:
        print(f"Error during form submission: {str(e)}")
        driver.quit()
        raise


@app.route('/generate_result', methods=['POST'])
def generate_result():
    data = request.get_json()
    exam_session = data.get('exam_session')
    course_type = data.get('course_type')
    exam_type = data.get('exam_type')
    course_name = data.get('course_name')
    semister = data.get('semister')
    roll_number = data.get('roll_number')

    if not exam_session or not course_type or not exam_type or not course_name or not semister or not roll_number:
        return jsonify({"error": "exam session, course type, exam type, course name, semister and roll number are required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result = open_website(driver, exam_session, course_type, exam_type, course_name, semister, roll_number)
        return jsonify({"message": "Result generated successfully", "screenshot": result.get("screenshot")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
