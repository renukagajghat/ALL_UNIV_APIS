
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pytesseract

def get_captcha_text(html, base_url):
    try:
        # Parse the HTML to find the CAPTCHA image URL
        soup = BeautifulSoup(html, 'html.parser')
        captcha_image_tag = soup.find('img', {'id': 'ctl00_cphBody_IMGCaptcha'})

        if not captcha_image_tag:
            raise ValueError("CAPTCHA image not found in the HTML")

        # Extract the src URL and convert it to an absolute URL
        captcha_url = captcha_image_tag['src']
        full_url = urljoin(base_url, captcha_url)

        # Download the CAPTCHA image
        response = requests.get(full_url)
        if response.status_code != 200:
            raise ValueError("Failed to fetch CAPTCHA image")

        # Open the image from the response content
        img = Image.open(BytesIO(response.content))

        # Ensure the image is in RGB mode (if not already)
        img = img.convert('RGB')

        # Save the original CAPTCHA image
        img.save('captcha_image.png')

        # Extract text from the CAPTCHA image using pytesseract
        custom_config = r'--oem 3 --psm 6'  # PSM 6 assumes a single block of text
        captcha_text = pytesseract.image_to_string(img, config=custom_config).strip()

        return captcha_text

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage
html = """<html><body><img id=\"ctl00_cphBody_IMGCaptcha\" aria-label=\"captchaimage\" aria-describedby=\"basic-captchaimage\" src=\"../CaptchaImage.aspx?query=0.5256648184267596&Code=CHD474\" style=\"height:50px;width:200px;border-width:0px;\"></body></html>"""
base_url = "https://ubse.upmsp.edu.in/"

captcha_text = get_captcha_text(html, base_url)
if captcha_text:
    print("Extracted CAPTCHA Text:", captcha_text)
else:
    print("Failed to extract CAPTCHA text.")


# Python code for solving an alphanumeric CAPTCHA

# import pytesseract
# from PIL import Image
# def solve_captcha(image_path):
#     captcha_image = Image.open(image_path)
#     captcha_text = pytesseract.image_to_string(captcha_image)
#     return captcha_text
# captcha_solution = solve_captcha('captcha_image.png')
# print("CAPTCHA Solution:", captcha_solution)