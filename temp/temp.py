#1. Make the imports
import requests, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

#2. Define a function that opens a link in new tab
def open_in_new_tab(browser, element):
    ActionChains(browser). \
    key_down(Keys.CONTROL). \
    click(element). \
    key_up(Keys.CONTROL). \
    perform()

#3. Open a controllable browser using Selenium webdriver module
profile = webdriver.FirefoxProfile()
profile.set_preference('webdriver_accept_untrusted_certs', True)
browser = webdriver.Firefox(firefox_profile = profile)

#4. Create wait object
waiting = WebDriverWait(browser,20)

#5. Open vtop home page
browser.get('http://vtop.vit.ac.in')

#6. Find the link to the vtopbeta page
try:
    vtopbeta_elem = browser.find_element_by_css_selector('a[href = "https://vtopbeta.vit.ac.in/vtop"] font b')
    print('Found element that href\'s to vtopbeta')
except:
    print('No element with attribute value a[href="https://vtopbeta.vit.ac.in/vtop"] was found')
    sys.exit()

#7. Open vtopbeta page in new tab and then switch tab
open_in_new_tab(browser, vtopbeta_elem)
waiting.until(lambda browser: len(browser.window_handles) == 2)
browser.switch_to_window(browser.window_handles[1]) # important!!

#8. Find the link to login page on vtopbeta captcha_img_elem and click on the elem to open the next page, ie, the login page
try:
    waiting.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn.btn-info.pull-right')))
    login_page_link_elem = browser.find_element_by_css_selector('.btn.btn-primary.pull-right')
except NoSuchElementException: #Exception as err:
    print('Check the css selector for the button leading to the login page: ' + str(err))
    sys.exit()
open_in_new_tab(browser, login_page_link_elem)
waiting.until(lambda browser: len(browser.window_handles) == 3)
browser.switch_to_window(browser.window_handles[2])

#9. From the login page, find the input elements (uname and pwd boxes and captcha box)
try:
    waiting.until(EC.presence_of_element_located((By.ID, 'captchaCheck')))
    username_elem = browser.find_element_by_css_selector('#uname')
    password_elem = browser.find_element_by_css_selector('#passwd')
    captcha_elem = browser.find_element_by_css_selector('#captchaCheck')
    captcha_img_elem = browser.find_element_by_css_selector('img[alt = "vtopCaptcha"]')
except:
    print('Input elements with the given css selectors were not found')
    sys.exit()

#10. Find the image source of the captcha image
captcha_img_src = captcha_img_elem.get_attribute('src')
print(captcha_img_src)

browser.quit()
