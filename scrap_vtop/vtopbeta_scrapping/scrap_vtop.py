#1. Make the imports
import requests, sys, pytesseract, base64, getpass, datetime, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from PIL import Image
from parser import CaptchaParse

#2. Read registration number, password and semester from user-inputs
registration_num = input('Enter registration number: ')
password = getpass.getpass('Enter password: ')
semester = input('Semester- Fall/Winter: ')
print('** make sure you enter correct registration number and password **')
if registration_num == '' or password == '' or semester == '':
    print('None of registration number, password, semester fields can be left empty.')
    sys.exit()

today = datetime.datetime.now()
semester = semester.capitalize() + ' Semester ' + str(today.year-1) + '-' + str(today.year%2000 + 1 - 1)
# print(semester)
# sys.exit()

print('Attempting to log you in...')

#3. Open a controllable browser using Selenium webdriver module
# profile = webdriver.FirefoxProfile()
# profile.set_preference('webdriver_accept_untrusted_certs', True)
# browser = webdriver.Firefox(firefox_profile = profile)
chromedriver = './chromedriver'
browser = webdriver.Chrome(chromedriver)
browser.maximize_window()
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

#15. Handle wrong reg/pwd inputs
# time.sleep(3)
# print(EC.visibility_of_element_located((By.CSS_SELECTOR, '.user=image')))
# if not EC.visibility_of_element_located((By.CSS_SELECTOR, '.user-image')):
#     print('Wrong registration number or password! Try again!')
#     sys.exit()

#TODO: scrapped the profile to obtain different informations- time table of currrent day, for eg
#14. Open the menu on the left using the toggle hamburger button- first find the button and then click
try:
    waiting.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[role = "button"]')))
except:
    print('VTOP taking too long to respond!')
    sys.exit()
hamburger_elem = browser.find_element_by_css_selector('a[role = "button"]')
hamburger_elem.click()

#15. Find the Academics option in the left menu and click on it
academics_elem = browser.find_element_by_css_selector('#dbMenu ul.sidebar-menu.tree>li:nth-child(2)')
academics_elem.click()

#16. Get the time table element and click on it
waiting.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#dbMenu ul.sidebar-menu.tree>li:nth-child(2) li:nth-child(2)>a span')))
timetable_elem = browser.find_element_by_css_selector('#dbMenu ul.sidebar-menu.tree>li:nth-child(2) li:nth-child(2)>a span')
timetable_elem.click()
hamburger_elem.click()

#17. Get the select element that has the list of semesters
waiting.until(EC.presence_of_element_located((By.ID, 'semesterSubId')))
selectsem_elem = browser.find_element_by_id('semesterSubId')
selectsem_elem_selectobj = Select(selectsem_elem)


#18. Select the semester as entered by the user from the list
selectsem_elem_selectobj.select_by_visible_text(semester)
selectsem_elem.submit()

#19. Make out daywise slots, find current day name, see what slots are there for the day
daywise_slots_th = {
    'Monday': ['A1','F1','D1','TB1','TG1','A2','F2','D2','TB2','TG2'],
    'Tuesday': ['B1','G1','E1','TC1','TAA1','B2','G2','E2','TC2','TAA2'],
    'Wednesday': ['C1','A1','F1','V1','V2','C2','A2','F2','TD2','TBB2'],
    'Thursday': ['D1','B1','G1','TE1','TCC1','D2','B2','G2','TE2','TCC2'],
    'Friday': ['E1','C1','TA1','TF1','TD1','E2','C2','TA2','TF2','TD2']
    # 'Saturday': ['V8','X1','Y1','X2','Z','Y2','W2','V9'],
    # 'Sunday': ['V10','Y1','X1','Y2','Z','X2','W2','V11']
}

daywise_slots_lab = {
    'Monday': ['L1','L2','L3','L4','L5','L6','L31','L32','L33','L34','L35','L36'],
    'Tuesday': ['L7','L8','L9','L10','L11','L12','L37','L38','L39','L40','L41','L42'],
    'Wednesday': ['L13','L14','L15','L16','L43','L44','L45','L46','L47','L48'],
    'Thursday': ['L19','L20','L21','L22','L23','L24','L49','L50','L51','L52','L53','L54'],
    'Friday': ['L25','L26','L27','L28','L29','L30','L55','L56','L57','L58','L59','L60']
}

day_timing_slots = ['8.00 - 8.50','9.00 - 9.50','10.00 - 10.50','11.00  11.50', \
    '12.00 - 12.50','2.00 - 2.50','03.00 - 3.50','4.00 - 4.50','5.00 - 5.50','6.00 - 6.50']

dayname_full = today.strftime('%A')
dayname_short = today.strftime('%a')
day_slots_th = daywise_slots_th[dayname_full]
daywise_slots_lab = daywise_slots_lab[dayname_full]

#20. Scrap time table for the day
day_of_the_week = today.strftime('%w')
day_of_the_week = int(day_of_the_week)
print('day num: ' + str(day_of_the_week))
row_nums_to_scrape = (2*day_of_the_week + 3, 2*day_of_the_week + 3)

th_row_to_scrape = browser.find_element_by_css_selector('#timeTableStyle tbody tr:nth-child(%d)' % row_nums_to_scrape[0])
lab_row_to_scrape = browser.find_element_by_css_selector('#timeTableStyle tbody tr:nth-child(%d)' % row_nums_to_scrape[1])
print(th_row_to_scrape)
print(lab_row_to_scrape)
