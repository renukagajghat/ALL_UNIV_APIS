# # from flask import Flask, request, jsonify
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.chrome.service import Service
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.webdriver.chrome.options import Options
# # from selenium.webdriver.support.ui import Select
# # from selenium.webdriver.common.action_chains import ActionChains
# # from datetime import datetime
# # import mysql.connector
# # import time
# # import os

# # # Set up Chrome options
# # chrome_options = Options()
# # chrome_options.add_argument("--disable-gpu")
# # chrome_options.add_argument("--no-sandbox")
# # chrome_options.add_argument("--disable-dev-shm-usage")
# # chrome_options.add_argument("--window-size=1920,1080")
# # chrome_options.add_argument("--ignore-certificate-errors")
# # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# # chrome_options.add_argument("--start-maximized")
# # # chrome_options.add_argument("--headless")  # Optional: Run in headless mode

# # # Setup the WebDriver (ensure you have the correct path to ChromeDriver)
# # service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# # app = Flask(__name__)

# # def save_filename_to_db(username, password, filename):
# #     """Save login details and the filename into the database."""
# #     try:
# #         # Connect to the database
# #         connection = mysql.connector.connect(
# #             host="localhost",
# #             user="root",
# #             password="",
# #             database="education_schema"
# #         )
# #         cursor = connection.cursor()

# #         # Insert data into the table, including the filename
# #         insert_query = """
# #         INSERT INTO login_details (login_value, password_value, filename)
# #         VALUES (%s, %s, %s)
# #         """
# #         cursor.execute(insert_query, (username, password, filename))

# #         # Commit the transaction
# #         connection.commit()
# #         print(f"Data saved successfully with file {filename}")

# #     except mysql.connector.Error as err:
# #         print(f"Error: {err}")
# #     finally:
# #         if connection.is_connected():
# #             cursor.close()
# #             connection.close()

# # def save_page_html(driver, filename):
# #     """Save the page HTML source."""
# #     page_source = driver.page_source
# #     with open(filename, 'w', encoding='utf-8') as file:
# #         file.write(page_source)
# #     print(f"Page source saved as {filename}")

# # def save_page_screenshot(driver, filename):
# #     """Save a screenshot of the page."""
# #     driver.save_screenshot(filename)
# #     print(f"Screenshot saved as {filename}")


# # # Define a function to determine the department based on the exam name
# # def get_department_for_exam(exam_name):
# #     """Map exam name to the appropriate department."""
# #     if "B. A" in exam_name or "M. A" in exam_name:
# #         return "Arts"
# #     elif "B. Com." in exam_name or "M. Com" in exam_name or "BBA" in exam_name or "MBA" in exam_name:
# #         return "Commerce"
# #     elif "B. Ed" in exam_name or "M. Ed" in exam_name:
# #         return "Education"
# #     elif "B. Tech" in exam_name or "M. Tech" in exam_name or "B. E." in exam_name:
# #         return "Engineering"
# #     elif "BFA" in exam_name or "MFA" in exam_name:
# #         return "Fine Arts"
# #     elif "LL. B" in exam_name or "LL. M" in exam_name:
# #         return "Law"
# #     elif "BBA" in exam_name or "MBA" in exam_name:
# #         return "Management"
# #     elif "MBBS" in exam_name or "BDS" in exam_name or "B.Pharm" in exam_name or "M.Pharm" in exam_name:
# #         return "Medical & Pharmaceutics"
# #     elif "B. Sc" in exam_name or "M. Sc" in exam_name or "Biotech" in exam_name:
# #         return "Science"
# #     return None  # Return None if no match is found

# # def close_modal_if_present(driver):
# #     """Close any modal overlay if it exists."""
# #     try:
# #         # Wait for a modal close button (if present) and click it
# #         close_button = WebDriverWait(driver, 5).until(
# #             EC.element_to_be_clickable((By.CLASS_NAME, "close"))
# #         )
# #         close_button.click()  # Close the modal
# #         print("Closed the modal overlay.")
# #     except Exception as e:
# #         print("No modal found or error while closing:", e)

# # def select_all_results(driver):
# #     """Select the 'All' option from the ResultList dropdown."""
# #     try:
# #         # Locate the dropdown element
# #         dropdown = WebDriverWait(driver, 10).until(
# #             EC.presence_of_element_located((By.NAME, "ResultList_length"))
# #         )
        
# #         # Use Select to choose the 'All' option
# #         select = Select(dropdown)
# #         select.select_by_value("-1")  # Select the 'All' option
        
# #         # Log the selection action
# #         print("Selected 'All' from the dropdown.")
        
# #         # Wait for the page to reload or update with all results
# #         WebDriverWait(driver, 10).until(
# #             EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ResultList']//tbody//tr"))
# #         )
# #         print("All results are now displayed on a single page.")
# #     except Exception as e:
# #         print(f"Error while selecting 'All' from the dropdown: {e}")

# # def navigate_to_exam_page(driver, exam_name):
# #     """Function to navigate and find the specific exam."""
# #     try:
# #         # Wait for the exam links to appear on the page
# #         exam_links = WebDriverWait(driver, 10).until(
# #             EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ResultList']//tbody//tr//a[contains(@href, 'index1.php?rid')]"))
# #         )

# #         # Log all the exams on the current page
# #         all_exams = [link.text for link in exam_links]
# #         print(f"Exams on current page: {all_exams}")
        
# #         # Check if the desired exam is on this page (case insensitive search)
# #         exams = [link for link in exam_links if exam_name.lower() in link.text.lower()]
# #         if exams:
# #             print(f"Exam '{exam_name}' found. Scrolling to and clicking the link.")
            
# #             # Scroll to the bottom of the page and back up to make sure the content is fully loaded
# #             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
# #             time.sleep(2)  # Let the page load
# #             driver.execute_script("window.scrollTo(0, 0);")  # Scroll back to the top
# #             time.sleep(2)  # Let the page load
            
# #             # Scroll to the element again and ensure it's visible in the viewport
# #             exam_link = exams[0]
# #             driver.execute_script("arguments[0].scrollIntoView(true);", exam_link)  # Scroll to the exam link
            
# #             # Add a short wait to ensure the link is clickable
# #             WebDriverWait(driver, 2).until(EC.element_to_be_clickable(exam_link))
            
# #             # Use JavaScript to click the link
# #             driver.execute_script("arguments[0].click();", exam_link)
# #             return True  # Exam found and navigated to result page
# #         else:
# #             print(f"Exam '{exam_name}' not found on the current page.")
# #             return False  # Exam not found 

# #     except Exception as e:
# #         print(f"Error while navigating to pages: {e}")
# #         return False


# # @app.route('/generate_result', methods=['POST'])
# # def generate_result():
# #     """Generates result by passing the exam name and roll number."""
# #     exam_name = request.json.get('exam_name')  # The exam name (provided via Postman)
# #     roll_number = request.json.get('roll_number')  # The student's roll number
    
# #     if not exam_name or not roll_number:
# #         return jsonify({"error": "Exam name and roll number are required"}), 400
    
# #     try:
# #         # Initialize WebDriver
# #         driver = webdriver.Chrome(service=service, options=chrome_options)
# #         driver.get("https://result.uniraj.ac.in/index1.php?rid=7756")  # Replace with the actual URL where exams are listed
        
# #         # Close any modal if present
# #         close_modal_if_present(driver)
        
# #         # Wait for the page to load and locate the "Undergraduate" link
# #         undergraduate_link = WebDriverWait(driver, 10).until(
# #             EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Undergraduate')]"))
# #         )
# #         undergraduate_link.click()

# #         # Wait for the branch dropdown to appear and select a branch based on the exam name
# #         department = get_department_for_exam(exam_name)
# #         if department is None:
# #             return jsonify({"error": "Unable to map the exam to a department"}), 400
        
# #         # Locate the dropdown menu and select the appropriate department
# #         branch_dropdown = WebDriverWait(driver, 10).until(
# #             EC.presence_of_element_located((By.CSS_SELECTOR, '.dropdown-menu'))
# #         )
        
# #         # Find the department option based on the department logic
# #         department_option = branch_dropdown.find_element(By.XPATH, f"//a[contains(text(), '{department}')]")
# #         department_option.click()

# #         # Select 'All' from the dropdown to show all exams
# #         select_all_results(driver)

# #         # Now, navigate through the pages to find the correct exam
# #         exam_found = navigate_to_exam_page(driver, exam_name)

# #         if exam_found:
# #             # Wait for the result page to load and find the roll number input field
# #             roll_number_field = WebDriverWait(driver, 10).until(
# #                 EC.presence_of_element_located((By.ID, 'rollno'))  # Adjust the ID if necessary
# #             )
# #             roll_number_field.send_keys(roll_number)

# #             # Locate and click the "Find" button to submit the form
# #             find_button = driver.find_element(By.NAME, 'OKbtn')  # Adjust button name if necessary
# #             find_button.click()

# #             # Wait for the result to be generated or error message to appear
# #             time.sleep(5)

# #             # Check if the error message is present
# #             error_message = driver.find_elements(By.XPATH, "//td[contains(text(), 'Please Enter Roll No. Correctly.(It Should be Number Only)')]")
# #             if error_message:
# #                 # If error message is present, return "No Data Found" message
# #                 return jsonify({"message": "No Data Found."}), 404

# #             # If result is generated, save a screenshot of the result page in the current working directory
# #             timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Format: "YYYY-MM-DD-HH-MM-SS"
# #             screenshot_filename = f"rajasthan_univ_result_{timestamp}.png"  # Append timestamp to filename
# #             screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
# #             driver.save_screenshot(screenshot_path)

# #             # Save the filename and other details to the database
# #             save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

# #             # Return the path of the saved screenshot
# #             return jsonify({"message": "Result generated successfully!", "screenshot_path": screenshot_path})

# #         else:
# #             return jsonify({"error": "Exam not found in the results list"}), 404

# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500
# #     finally:
# #         driver.quit()


# # if __name__ == '__main__':
# #     app.run(debug=True)






# from flask import Flask, request, jsonify
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.action_chains import ActionChains
# from datetime import datetime
# import mysql.connector
# import time
# import os

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--ignore-certificate-errors")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--start-maximized")
# # chrome_options.add_argument("--headless")  # Optional: Run in headless mode

# # Setup the WebDriver (ensure you have the correct path to ChromeDriver)
# service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# app = Flask(__name__)

# def save_filename_to_db(username, password, filename):
#     """Save login details and the filename into the database."""
#     try:
#         # Connect to the database
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="education_schema"
#         )
#         cursor = connection.cursor()

#         # Insert data into the table, including the filename
#         insert_query = """
#         INSERT INTO login_details (login_value, password_value, filename)
#         VALUES (%s, %s, %s)
#         """
#         cursor.execute(insert_query, (username, password, filename))

#         # Commit the transaction
#         connection.commit()
#         print(f"Data saved successfully with file {filename}")

#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()

# def save_page_html(driver, filename):
#     """Save the page HTML source."""
#     page_source = driver.page_source
#     with open(filename, 'w', encoding='utf-8') as file:
#         file.write(page_source)
#     print(f"Page source saved as {filename}")

# def save_page_screenshot(driver, filename):
#     """Save a screenshot of the page."""
#     driver.save_screenshot(filename)
#     print(f"Screenshot saved as {filename}")


# # # Define a function to determine the department based on the exam name
# # def get_department_for_exam(exam_name):
# #     """Map exam name to the appropriate department."""
# #     if "B. A" in exam_name or "M. A" in exam_name:
# #         return "Arts"
# #     elif "B. Com." in exam_name or "M. Com" in exam_name or "BBA" in exam_name or "MBA" in exam_name:
# #         return "Commerce"
# #     elif "B. Ed" in exam_name or "M. Ed" in exam_name:
# #         return "Education"
# #     elif "B. Tech" in exam_name or "M. Tech" in exam_name or "B. E." in exam_name:
# #         return "Engineering"
# #     elif "BFA" in exam_name or "MFA" in exam_name:
# #         return "Fine Arts"
# #     elif "LL. B" in exam_name or "LL. M" in exam_name:
# #         return "Law"
# #     elif "BBA" in exam_name or "MBA" in exam_name:
# #         return "Management"
# #     elif "MBBS" in exam_name or "BDS" in exam_name or "B.Pharm" in exam_name or "M.Pharm" in exam_name:
# #         return "Medical & Pharmaceutics"
# #     elif "B. Sc" in exam_name or "M. Sc" in exam_name or "Biotech" in exam_name:
# #         return "Science"
# #     return None  # Return None if no match is found

# def close_modal_if_present(driver):
#     """Close any modal overlay if it exists."""
#     try:
#         # Wait for a modal close button (if present) and click it
#         close_button = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.CLASS_NAME, "close"))
#         )
#         close_button.click()  # Close the modal
#         print("Closed the modal overlay.")
#     except Exception as e:
#         print("No modal found or error while closing:", e)

# def select_all_results(driver):
#     """Select the 'All' option from the ResultList dropdown."""
#     try:
#         # Locate the dropdown element
#         dropdown = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.NAME, "ResultList_length"))
#         )
        
#         # Use Select to choose the 'All' option
#         select = Select(dropdown)
#         select.select_by_value("-1")  # Select the 'All' option
        
#         # Log the selection action
#         print("Selected 'All' from the dropdown.")
        
#         # Wait for the page to reload or update with all results
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ResultList']//tbody//tr"))
#         )
#         print("All results are now displayed on a single page.")
#     except Exception as e:
#         print(f"Error while selecting 'All' from the dropdown: {e}")

# def navigate_to_exam_page(driver, exam_link):
#     """Navigate to the provided exam link."""
#     try:
#         # Wait for all rows in the results table to load
#         rows = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ResultList']//tbody//tr"))
#         )

#         # Log available links
#         print("Available exam links:")
#         for row in rows:
#             link_element = row.find_element(By.XPATH, ".//a")
#             href = link_element.get_attribute("href")
#             print(f"Found link: {href}")  # Log the actual href

#         # Iterate through the rows to find the matching link
#         for row in rows:
#             link_element = row.find_element(By.XPATH, ".//a")
#             href = link_element.get_attribute("href")
#             if exam_link in href:
#                 print(f"Exam link '{exam_link}' found. Clicking on it using JavaScript.")

#                 # Use JavaScript to click the link
#                 driver.execute_script("arguments[0].click();", link_element)
#                 return True

#         # If the loop completes and no link matches
#         print(f"Exam link '{exam_link}' not found on the current page.")
#         return False

#     except Exception as e:
#         print(f"Error while navigating to the exam link: {e}")
#         return False


# @app.route('/generate_result', methods=['POST'])
# def generate_result():
#     """Generates result by passing the exam name, year, and roll number."""
#     # exam_name = request.json.get('exam_name')  # The exam name 
#     # exam_year = request.json.get('exam_year')  # The exam year 
#     exam_link = request.json.get('exam_link')
#     roll_number = request.json.get('roll_number')  # The student's roll number
    
#     if not roll_number or not exam_link:
#         return jsonify({"error": "Exam link and roll number are required"}), 400


#     try:
#         # Initialize WebDriver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.get("https://result.uniraj.ac.in/index1.php?rid=7756")  # Replace with the actual URL where exams are listed
        
#         # Close any modal if present
#         close_modal_if_present(driver)
        
#         # # Wait for the page to load and locate the "Undergraduate" link
#         # undergraduate_link = WebDriverWait(driver, 10).until(
#         #     EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Undergraduate')]"))
#         # )
#         # undergraduate_link.click()

#         # # Wait for the branch dropdown to appear and select a branch based on the exam name
#         # department = get_department_for_exam(exam_name)
#         # if department is None:
#         #     return jsonify({"error": "Unable to map the exam to a department"}), 400
        
#         # # Locate the dropdown menu and select the appropriate department
#         # branch_dropdown = WebDriverWait(driver, 10).until(
#         #     EC.presence_of_element_located((By.CSS_SELECTOR, '.dropdown-menu'))
#         # )
        
#         # # Find the department option based on the department logic
#         # department_option = branch_dropdown.find_element(By.XPATH, f"//a[contains(text(), '{department}')]")
#         # department_option.click()

#         # Select 'All' from the dropdown to show all exams
#         select_all_results(driver)

#         # Now, navigate through the pages to find the correct exam
#         exam_found = navigate_to_exam_page(driver, exam_link)

#         if exam_found:
#             # Wait for the result page to load and find the roll number input field
#             roll_number_field = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.ID, 'rollno'))  # Adjust the ID if necessary
#             )
#             roll_number_field.send_keys(roll_number)

#             # Locate and click the "Find" button to submit the form
#             find_button = driver.find_element(By.NAME, 'OKbtn')  # Adjust button name if necessary
#             find_button.click()

#             # Wait for the result to be generated or error message to appear
#             time.sleep(5)

#             # Check if the error message is present
#             error_message = driver.find_elements(By.XPATH, "//td[contains(text(), 'Please Enter Roll No. Correctly.(It Should be Number Only)')]")
#             if error_message:
#                 # If error message is present, return "No Data Found" message
#                 return jsonify({"message": "No Data Found."}), 404

#             # If result is generated, save a screenshot of the result page in the current working directory
#             timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Format: "YYYY-MM-DD-HH-MM-SS"
#             screenshot_filename = f"rajasthan_univ_result_{timestamp}.png"  # Append timestamp to filename
#             screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
#             driver.save_screenshot(screenshot_path)

#             # Save the filename and other details to the database
#             save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

#             # Return the path of the saved screenshot
#             return jsonify({"message": "Result generated successfully!", "screenshot_path": screenshot_path})

#         else:
#             return jsonify({"error": "Exam not found in the results list"}), 404

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         driver.quit()

# if __name__ == '__main__':
#     app.run(debug=True)







# from flask import Flask, request, jsonify
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.action_chains import ActionChains
# from datetime import datetime
# import mysql.connector
# import time
# import os

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--ignore-certificate-errors")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--start-maximized")
# # chrome_options.add_argument("--headless")  # Optional: Run in headless mode

# # Setup the WebDriver (ensure you have the correct path to ChromeDriver)
# service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# app = Flask(__name__)

# def save_filename_to_db(username, password, filename):
#     """Save login details and the filename into the database."""
#     try:
#         # Connect to the database
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="education_schema"
#         )
#         cursor = connection.cursor()

#         # Insert data into the table, including the filename
#         insert_query = """
#         INSERT INTO login_details (login_value, password_value, filename)
#         VALUES (%s, %s, %s)
#         """
#         cursor.execute(insert_query, (username, password, filename))

#         # Commit the transaction
#         connection.commit()
#         print(f"Data saved successfully with file {filename}")

#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()

# def save_page_html(driver, filename):
#     """Save the page HTML source."""
#     page_source = driver.page_source
#     with open(filename, 'w', encoding='utf-8') as file:
#         file.write(page_source)
#     print(f"Page source saved as {filename}")

# def save_page_screenshot(driver, filename):
#     """Save a screenshot of the page."""
#     driver.save_screenshot(filename)
#     print(f"Screenshot saved as {filename}")


# # Define a function to determine the department based on the exam name
# def get_department_for_exam(exam_name):
#     """Map exam name to the appropriate department."""
#     if "B. A" in exam_name or "M. A" in exam_name:
#         return "Arts"
#     elif "B. Com." in exam_name or "M. Com" in exam_name or "BBA" in exam_name or "MBA" in exam_name:
#         return "Commerce"
#     elif "B. Ed" in exam_name or "M. Ed" in exam_name:
#         return "Education"
#     elif "B. Tech" in exam_name or "M. Tech" in exam_name or "B. E." in exam_name:
#         return "Engineering"
#     elif "BFA" in exam_name or "MFA" in exam_name:
#         return "Fine Arts"
#     elif "LL. B" in exam_name or "LL. M" in exam_name:
#         return "Law"
#     elif "BBA" in exam_name or "MBA" in exam_name:
#         return "Management"
#     elif "MBBS" in exam_name or "BDS" in exam_name or "B.Pharm" in exam_name or "M.Pharm" in exam_name:
#         return "Medical & Pharmaceutics"
#     elif "B. Sc" in exam_name or "M. Sc" in exam_name or "Biotech" in exam_name:
#         return "Science"
#     return None  # Return None if no match is found

# def close_modal_if_present(driver):
#     """Close any modal overlay if it exists."""
#     try:
#         # Wait for a modal close button (if present) and click it
#         close_button = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.CLASS_NAME, "close"))
#         )
#         close_button.click()  # Close the modal
#         print("Closed the modal overlay.")
#     except Exception as e:
#         print("No modal found or error while closing:", e)

# def select_all_results(driver):
#     """Select the 'All' option from the ResultList dropdown."""
#     try:
#         # Locate the dropdown element
#         dropdown = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.NAME, "ResultList_length"))
#         )
        
#         # Use Select to choose the 'All' option
#         select = Select(dropdown)
#         select.select_by_value("-1")  # Select the 'All' option
        
#         # Log the selection action
#         print("Selected 'All' from the dropdown.")
        
#         # Wait for the page to reload or update with all results
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ResultList']//tbody//tr"))
#         )
#         print("All results are now displayed on a single page.")
#     except Exception as e:
#         print(f"Error while selecting 'All' from the dropdown: {e}")

# def navigate_to_exam_page(driver, exam_name):
#     """Function to navigate and find the specific exam."""
#     try:
#         # Wait for the exam links to appear on the page
#         exam_links = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ResultList']//tbody//tr//a[contains(@href, 'index1.php?rid')]"))
#         )

#         # Log all the exams on the current page
#         all_exams = [link.text for link in exam_links]
#         print(f"Exams on current page: {all_exams}")
        
#         # Check if the desired exam is on this page (case insensitive search)
#         exams = [link for link in exam_links if exam_name.lower() in link.text.lower()]
#         if exams:
#             print(f"Exam '{exam_name}' found. Scrolling to and clicking the link.")
            
#             # Scroll to the bottom of the page and back up to make sure the content is fully loaded
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
#             time.sleep(2)  # Let the page load
#             driver.execute_script("window.scrollTo(0, 0);")  # Scroll back to the top
#             time.sleep(2)  # Let the page load
            
#             # Scroll to the element again and ensure it's visible in the viewport
#             exam_link = exams[0]
#             driver.execute_script("arguments[0].scrollIntoView(true);", exam_link)  # Scroll to the exam link
            
#             # Add a short wait to ensure the link is clickable
#             WebDriverWait(driver, 2).until(EC.element_to_be_clickable(exam_link))
            
#             # Use JavaScript to click the link
#             driver.execute_script("arguments[0].click();", exam_link)
#             return True  # Exam found and navigated to result page
#         else:
#             print(f"Exam '{exam_name}' not found on the current page.")
#             return False  # Exam not found 

#     except Exception as e:
#         print(f"Error while navigating to pages: {e}")
#         return False


# @app.route('/generate_result', methods=['POST'])
# def generate_result():
#     """Generates result by passing the exam name and roll number."""
#     exam_name = request.json.get('exam_name')  # The exam name (provided via Postman)
#     roll_number = request.json.get('roll_number')  # The student's roll number
    
#     if not exam_name or not roll_number:
#         return jsonify({"error": "Exam name and roll number are required"}), 400
    
#     try:
#         # Initialize WebDriver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.get("https://result.uniraj.ac.in/index1.php?rid=7756")  # Replace with the actual URL where exams are listed
        
#         # Close any modal if present
#         close_modal_if_present(driver)
        
#         # Wait for the page to load and locate the "Undergraduate" link
#         undergraduate_link = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Undergraduate')]"))
#         )
#         undergraduate_link.click()

#         # Wait for the branch dropdown to appear and select a branch based on the exam name
#         department = get_department_for_exam(exam_name)
#         if department is None:
#             return jsonify({"error": "Unable to map the exam to a department"}), 400
        
#         # Locate the dropdown menu and select the appropriate department
#         branch_dropdown = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '.dropdown-menu'))
#         )
        
#         # Find the department option based on the department logic
#         department_option = branch_dropdown.find_element(By.XPATH, f"//a[contains(text(), '{department}')]")
#         department_option.click()

#         # Select 'All' from the dropdown to show all exams
#         select_all_results(driver)

#         # Now, navigate through the pages to find the correct exam
#         exam_found = navigate_to_exam_page(driver, exam_name)

#         if exam_found:
#             # Wait for the result page to load and find the roll number input field
#             roll_number_field = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.ID, 'rollno'))  # Adjust the ID if necessary
#             )
#             roll_number_field.send_keys(roll_number)

#             # Locate and click the "Find" button to submit the form
#             find_button = driver.find_element(By.NAME, 'OKbtn')  # Adjust button name if necessary
#             find_button.click()

#             # Wait for the result to be generated or error message to appear
#             time.sleep(5)

#             # Check if the error message is present
#             error_message = driver.find_elements(By.XPATH, "//td[contains(text(), 'Please Enter Roll No. Correctly.(It Should be Number Only)')]")
#             if error_message:
#                 # If error message is present, return "No Data Found" message
#                 return jsonify({"message": "No Data Found."}), 404

#             # If result is generated, save a screenshot of the result page in the current working directory
#             timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Format: "YYYY-MM-DD-HH-MM-SS"
#             screenshot_filename = f"rajasthan_univ_result_{timestamp}.png"  # Append timestamp to filename
#             screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
#             driver.save_screenshot(screenshot_path)

#             # Save the filename and other details to the database
#             save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

#             # Return the path of the saved screenshot
#             return jsonify({"message": "Result generated successfully!", "screenshot_path": screenshot_path})

#         else:
#             return jsonify({"error": "Exam not found in the results list"}), 404

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         driver.quit()


# if __name__ == '__main__':
#     app.run(debug=True)






from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import mysql.connector
import time
import os

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")  # Optional: Run in headless mode

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

def save_page_html(driver, filename):
    """Save the page HTML source."""
    page_source = driver.page_source
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(page_source)
    print(f"Page source saved as {filename}")

def save_page_screenshot(driver, filename):
    """Save a screenshot of the page."""
    driver.save_screenshot(filename)
    print(f"Screenshot saved as {filename}")

def close_modal_if_present(driver):
    """Close any modal overlay if it exists."""
    try:
        # Wait for a modal close button (if present) and click it
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "close"))
        )
        close_button.click()  # Close the modal
        print("Closed the modal overlay.")
    except Exception as e:
        print("No modal found or error while closing:", e)

@app.route('/generate_result', methods=['POST'])
def generate_result():
    """Generates result by passing the exam name, year, and roll number."""
    exam_link = request.json.get('exam_link')
    roll_number = request.json.get('roll_number')  # The student's roll number
    
    if not roll_number or not exam_link:
        return jsonify({"error": "Exam link and roll number are required"}), 400


    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://result.uniraj.ac.in/index1.php?rid=7782")  # Replace with the actual URL where exams are listed
        
        # Close any modal if present
        close_modal_if_present(driver)
        

        if exam_link:
            # Wait for the result page to load and find the roll number input field
            roll_number_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'rollno'))  # Adjust the ID if necessary
            )
            roll_number_field.send_keys(roll_number)

            # Locate and click the "Find" button to submit the form
            find_button = driver.find_element(By.NAME, 'OKbtn')  # Adjust button name if necessary
            find_button.click()

            # Wait for the result to be generated or error message to appear
            time.sleep(5)

            # Check if the error message is present
            error_message = driver.find_elements(By.XPATH, "//td[contains(text(), 'Please Enter Roll No. Correctly.(It Should be Number Only)')]")
            if error_message:
                # If error message is present, return "No Data Found" message
                return jsonify({"message": "No Data Found."}), 404

            # If result is generated, save a screenshot of the result page in the current working directory
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Format: "YYYY-MM-DD-HH-MM-SS"
            screenshot_filename = f"rajasthan_univ_result_{timestamp}.png"  # Append timestamp to filename
            screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
            driver.save_screenshot(screenshot_path)

            # Save the filename and other details to the database
            save_filename_to_db('finance@mistitservices.com', '1234mkM#', screenshot_filename)

            # Return the path of the saved screenshot
            return jsonify({"message": "Result generated successfully!", "screenshot_path": screenshot_path})

        else:
            return jsonify({"error": "Exam link not found in the results list"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)






