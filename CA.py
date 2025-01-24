# from flask import Flask, request, jsonify
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import mysql.connector
# import time
# from datetime import datetime

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
# chrome_options.add_argument('--headless')


# # Setup the web driver
# service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# # Flask app initialization
# app = Flask(__name__)

# def save_user_details_to_db(name, gender, qualification, address, cop_status, associate_year):
#     """Save user details into the database."""
#     try:
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="education_schema"
#         )
#         cursor = connection.cursor()

#         # Insert data into the table
#         insert_query = """
#         INSERT INTO ca_student_details (name, gender, qualification, address, cop_status, associate_year)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(insert_query, (name, gender, qualification, address, cop_status, associate_year))

#         # Commit the transaction
#         connection.commit()
#         print(f"CA student details saved successfully for: {name}")

#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()


# def open_website(driver, membership_number):
#     try:
#         driver.get('http://112.133.194.254/lom.asp')

#         # Enter membership number
#         membership_number_input = driver.find_element(By.NAME, 't1')
#         membership_number_input.send_keys(membership_number)

#         try:
#             print("Attempting to locate submit button...")
#             submit_button = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.XPATH, "//input[@type='Submit' and @value='Submit']"))
#             )
#             print("Submit button found and clickable.")
#             driver.execute_script("arguments[0].click();", submit_button)

#         except Exception as e:
#             print(f"Error locating or interacting with submit button: {str(e)}")

#         # Wait for the result to load
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.XPATH, "//table[contains(@border, '0')]"))
#         )

#         # Extract the details from the page
#         try:
#             # Extract Name, Gender, and Qualification
#             name_full = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Name')]]/td[2]").text.strip()
#             gender = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Gender')]]/td[2]").text.strip()
#             qualification_full = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Qualification')]]/td[2]").text.strip()

#             # Extract Address - First line 
#             address_xpath = "//tr[td[contains(text(), 'Address')]]/td[2]"
#             first_address_line = driver.find_element(By.XPATH, address_xpath).text.strip()

#             # Other address lines (skip rows containing COP Status and Associate Year)
#             address_lines = [first_address_line]
            
#             # Get other address rows explicitly skipping COP Status and Associate Year
#             address_rows = driver.find_elements(By.XPATH, "//tr[td[contains(text(), 'Address')]]/following-sibling::tr/td[2]")
#             for row in address_rows:
#                 address_text = row.text.strip()
#                 # Skip the COP Status or Associate Year rows
#                 if address_text and "COP Status" not in address_text and "Associate Year" not in address_text:
#                     address_lines.append(address_text)

#             # Join the address lines with newline to preserve line breaks
#             address = "\n".join(address_lines)

#             # Extract COP Status and Associate Year separately
#             cop_status = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'COP Status')]]/td[2]").text.strip()
#             associate_year = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Associate Year')]]/td[2]").text.strip()

#             # Split name and qualification
#             name_parts = name_full.split(",")
#             name = name_parts[0].strip()  # Take the first part as the name
#             qualification = name_parts[1].strip() if len(name_parts) > 1 else "Unknown"  # Default to "Unknown" if not found

#             # Save user details to the database
#             save_user_details_to_db(name, gender, qualification, address, cop_status, associate_year)

#             # Return result as a dictionary
#             return {
#                 "status": True,
#                 "message": "Result generated successfully",
#                 "name": name,
#                 "gender": gender,
#                 "qualification": qualification,
#                 "address": address,
#                 "cop_status": cop_status,
#                 "associate_year": associate_year
#             }
#         except Exception as e:
#             print(f"Error extracting data from the page: {str(e)}")
#             return {
#                 "status": False,
#                 "message": f"Error extracting data: {str(e)}"
#             }

#     except Exception as e:
#         print(f"Error during form submission: {str(e)}")
#         driver.quit()
#         raise


# @app.route('/generate_result', methods=['POST'])
# def generate_result():
#     data = request.get_json()
#     membership_number = data.get('membership_number')

#     if not membership_number:
#         return jsonify({"error": "Membership number is required"}), 400

#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     try:
#         result_data = open_website(driver, membership_number)
#         return jsonify(result_data)
    
#     except Exception as e:
#         error_message = str(e)
#         print(f"Error: {e}")
#         return jsonify({"message": "An issue occurred while processing your request.", "status": False}), 500
#     finally:
#         driver.quit()


# if __name__ == '__main__':
#     app.run(debug=True)







from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import time
from datetime import datetime

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
chrome_options.add_argument('--headless')


# Setup the web driver
service = Service(executable_path='C:/Users/renuka/chromedriver.exe')

# Flask app initialization
app = Flask(__name__)

def save_user_details_to_db(name, gender, qualification, address, cop_status, associate_year):
    """Save user details into the database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="education_schema"
        )
        cursor = connection.cursor()

        # Insert data into the table
        insert_query = """
        INSERT INTO ca_student_details (name, gender, qualification, address, cop_status, associate_year)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, gender, qualification, address, cop_status, associate_year))

        # Commit the transaction
        connection.commit()
        print(f"CA student details saved successfully for: {name}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


import re

def open_website(driver, membership_number):
    try:
        driver.get('http://112.133.194.254/lom.asp')

        # Enter membership number
        membership_number_input = driver.find_element(By.NAME, 't1')
        membership_number_input.send_keys(membership_number)

        try:
            print("Attempting to locate submit button...")
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='Submit' and @value='Submit']"))
            )
            print("Submit button found and clickable.")
            driver.execute_script("arguments[0].click();", submit_button)

        except Exception as e:
            print(f"Error locating or interacting with submit button: {str(e)}")

        # Wait for the result to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@border, '0')]"))
        )

        # Extract the details from the page
        try:
            # Extract Name, Gender, and Qualification
            name_full = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Name')]]/td[2]").text.strip()
            gender = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Gender')]]/td[2]").text.strip()
            qualification_full = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Qualification')]]/td[2]").text.strip()

            # Extract Address - First line 
            address_xpath = "//tr[td[contains(text(), 'Address')]]/td[2]"
            first_address_line = driver.find_element(By.XPATH, address_xpath).text.strip()

            # Initialize address_lines with the first address line
            address_lines = [first_address_line]
            
            # Get other address rows explicitly skipping COP Status and Associate Year
            address_rows = driver.find_elements(By.XPATH, "//tr[td[contains(text(), 'Address')]]/following-sibling::tr/td[2]")
            for row in address_rows:
                address_text = row.text.strip()

                # Skip the rows containing COP Status or Associate Year
                if "COP Status" in address_text or "Associate Year" in address_text:
                    continue  # Skip the COP Status and Associate Year rows

                # Add other valid address rows
                if address_text:
                    address_lines.append(address_text)

            # Join the address lines with newline to preserve line breaks
            full_address = "\n".join(address_lines)

            parts = full_address.split('\n')
            trimmed_parts = parts[:-2]
            address = ' '.join(trimmed_parts)

            # # Try to match the pincode (which is expected to be a 6-digit number at the end of the address)
            # match = re.search(r'(\d{6})\s*$', full_address)

            # if match:
            #     # We have matched the pincode, we will remove the lines after it
            #     address_with_pincode = full_address[:match.start()].strip()  # Keep address before pincode
            #     pincode = match.group(1)
            # else:
            #     # If no pincode is found, return full address without trimming
            #     address_with_pincode = full_address.strip()
            #     pincode = ""

            # # Remove the lines with COP Status and Associate Year if they are part of the address
            # address_with_pincode = "\n".join([line for line in address_with_pincode.split('\n') if "COP Status" not in line and "Associate Year" not in line])

            # Extract COP Status and Associate Year separately
            cop_status = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'COP Status')]]/td[2]").text.strip()
            associate_year = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Associate Year')]]/td[2]").text.strip()

            # Split name and qualification
            name_parts = name_full.split(",")
            name = name_parts[0].strip()  # Take the first part as the name
            qualification = name_parts[1].strip() if len(name_parts) > 1 else "Unknown"  # Default to "Unknown" if not found

            # Save user details to the database
            save_user_details_to_db(name, gender, qualification, address, cop_status, associate_year)

            # Return result as a dictionary
            return {
                "status": True,
                "message": "Result generated successfully",
                "name": name,
                "gender": gender,
                "qualification": qualification,
                "address": address,  # Address with pincode only, without COP Status and Associate Year
                "cop_status": cop_status,
                "associate_year": associate_year
            }
        except Exception as e:
            print(f"Error extracting data from the page: {str(e)}")
            return {
                "status": False,
                "message": f"Error extracting data: {str(e)}"
            }

    except Exception as e:
        print(f"Error during form submission: {str(e)}")
        driver.quit()
        raise



@app.route('/generate_result', methods=['POST'])
def generate_result():
    data = request.get_json()
    membership_number = data.get('membership_number')

    if not membership_number:
        return jsonify({"error": "Membership number is required"}), 400

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        result_data = open_website(driver, membership_number)
        return jsonify(result_data)
    
    except Exception as e:
        error_message = str(e)
        print(f"Error: {e}")
        return jsonify({"message": "An issue occurred while processing your request.", "status": False}), 500
    finally:
        driver.quit()


if __name__ == '__main__':
    app.run(debug=True)

















