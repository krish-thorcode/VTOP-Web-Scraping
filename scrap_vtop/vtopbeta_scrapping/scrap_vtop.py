#1. Make the imports
import requests, sys, pytesseract, base64, getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from parser import CaptchaParse

#2. Read registration number and password from user-inputs
registration_num = input('Enter username: ')
password = getpass.getpass('Enter password: ')
print('Connecting...')
print('Opening browser...')

#3. Open a controllable browser using Selenium webdriver module
profile = webdriver.FirefoxProfile()
profile.set_preference('webdriver_accept_untrusted_certs', True)
browser = webdriver.Firefox(firefox_profile = profile)

#4. Create wait object
waiting = WebDriverWait(browser,300)

#5. Open vtop home page
try:
    browser.get('http://vtop.vit.ac.in')
except:
    print('Check your internet connection!')
    sys.exit()

#6. Find the link to the vtopbeta page
try:
    vtopbeta_elem = browser.find_element_by_css_selector('a[href = "https://vtopbeta.vit.ac.in/vtop"] font b')
    # print('Found element that href\'s to vtopbeta')
except:
    print('No element with attribute value a[href="https://vtopbeta.vit.ac.in/vtop"] was found')
    sys.exit()

#7. Open vtopbeta
browser.get(vtopbeta_elem.text)

#8. Find the link to login page on vtopbeta captcha_img_elem and click on the elem to open the next page, ie, the login page
try:
    login_page_link_elem = browser.find_element_by_css_selector('.btn.btn-primary.pull-right')
    # print('Found element that href\'s to the login page')
except NoSuchElementException:
    print('Check the css selector for the button leading to the login page: ' + str(err))
    sys.exit()

login_page_link_elem.click()
waiting.until(lambda browser: len(browser.window_handles) == 2)
browser.switch_to_window(browser.window_handles[1])

#9. From the login page, find the input elements (uname and pwd boxes and captcha box)
try:
    waiting.until(EC.presence_of_element_located((By.ID, 'captchaCheck')))
    username_elem = browser.find_element_by_css_selector('#uname')
    # print('Acquired the uname textbox')
    password_elem = browser.find_element_by_css_selector('#passwd')
    # print('Acquired the password textbox')
    captcha_elem = browser.find_element_by_css_selector('#captchaCheck')
    # print('Acquired the captcha textbox')
    captcha_img_elem = browser.find_element_by_css_selector('img[alt = "vtopCaptcha"]')
except NoSuchElementException as err:
    print('Input elements with the given css selectors were not found: ' + err)
    sys.exit()

#10. Find the image source of the captcha image
captcha_img_src = captcha_img_elem.get_attribute('src')
# print(captcha_img_src)

#11. Extract the base64 stribg of the captcha image from the captcha_img_src
base64_img = captcha_img_src[22:]
# print(base64_img)

#12. Save the captcha image
captcha_img = open('./captcha_save/captcha.png','wb')
captcha_img.write(base64.b64decode(base64_img))
captcha_img.close()

#13. Convert the image into string
img = Image.open('./captcha_save/captcha.png')
captcha_str = CaptchaParse(img)
# print(captcha_str)

#13. Fill in login details
username_elem.send_keys(registration_num)
password_elem.send_keys(password)
captcha_elem.send_keys(captcha_str)

#14. Sign in
# note: the form doesn't have a submit button, the sign in button is not the submit button
# so maybe that is why using submit method on form elements leads to a page that doesn't exist
signin_button = browser.find_element_by_css_selector('.btn.btn-primary.pull-right')
signin_button.click()

#TODO: scrapped the profile to obtain different informations- time table of currrent day, for eg
#14. Open the menu on the left using the toggle hamburger button- first find the button and then click
waiting.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[role = "button"]')))
hamburger_elem = browser.find_element_by_css_selector('a[role = "button"]')
hamburger_elem.click()
# browser.quit()

#15. Find the Academics option in the left menu and click on it
academics_elem = browser.find_element_by_css_selector('#dbMenu ul.sidebar-menu.tree>li:nth-child(2)')
academics_elem.click()
