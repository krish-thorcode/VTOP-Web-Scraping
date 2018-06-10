#1. Make the imports

import requests, sys
from selenium import webdriver


#2. Open a controllable browser using Selenium webdriver module
browser = webdriver.Firefox()

#3. Open vtop home page
browser.get('http://vtop.vit.ac.in')

#4. Find the link to the vtopbeta page
try:
    vtopbeta_elem = browser.find_element_by_css_selector('a[href = "https://vtopbeta.vit.ac.in/vtop"] font b')
    print('Found element that href\'s to vtopbeta')
except:
    print('No element with attribute value a[href="https://vtopbeta.vit.ac.in/vtop"] was found')
    sys.exit()

#5. Open vtopbeta pag
browser.get(vtopbeta_elem.text)

#6. Find the link to login page on vtopbeta captcha_img_elem and click on the elem to open the next page, ie, the login page
try:
    login_page_link_elem = browser.find_element_by_css_selector('.btn.btn-primary.pull-right')
except:
    print('Check the css selector for the button leading to the login page')
    sys.exit()
login_page_link_elem.click()

#7. From the login page, find the input elements (uname and pwd boxes and captcha box)
try:
    username_elem = browser.find_element_by_css_selector('#uname')
    password_elem = browser.find_element_by_css_selector('#passwd')
    captcha_elem = browser.find_element_by_css_selector()
    captcha_img_elem = browser.find_element_by_css_selector('img[alt = "vtopCaptcha"]')
except:
    print('Input elements with the given css selectors were not found')
    sys.exit()

#8. Find the image source of the captcha image
captcha_img_src = captcha_img_elem.get_attribute('src')
print(captcha_img_src)

browser.quit()
