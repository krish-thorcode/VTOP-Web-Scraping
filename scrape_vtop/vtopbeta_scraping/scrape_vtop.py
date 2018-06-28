# Make the imports
import requests, sys, pytesseract, base64, getpass, datetime, time, threading, platform, os, argparse, shelve
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.support.ui import Select
from PIL import Image
from parser import CaptchaParse
from source_of_functions import *


#1. Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--newuser', help= 'Give this option if you are loggin in for the first time or \
                    you want to login into a new account.', action = 'store_true')
args = parser.parse_args()

#2. Read registration number, password and semester from user-inputs if this is first time login or new login
# and also shelve the credentials
if args.newuser:
    registration_num = input('Enter registration number: ')
    password = getpass.getpass('Enter password: ')

    if registration_num == '' or password == '':
        print('None of registration number, password, semester fields can be left empty.')
        sys.exit()

    print('** make sure you enter correct registration number and password **')

    shelf_file = shelve.open('./shelf/shelf_file')
    shelf_file['registration_num'] = registration_num
    shelf_file['password'] = password
    shelf_file.close()
else:
    shelf_file = shelve.open('./shelf/shelf_file')
    registration_num = shelf_file['registration_num']
    password = shelf_file['password']
    shelf_file.close()

today = datetime.datetime.now()

print('Attempting to log you in...')

#3. Open a controllable browser using Selenium webdriver module with a custom download directory
chrome_options = webdriver.ChromeOptions()
download_dir = find_download_dir()
prefs = {'download.default_directory': download_dir + '/temp'}
chrome_options.add_experimental_option('prefs', prefs)
chromedriver = './chromedriver'
browser = webdriver.Chrome(executable_path=chromedriver, chrome_options = chrome_options)
browser.maximize_window()

#4. Create wait object
waiting = WebDriverWait(browser,300)

#5. Open vtop home page
try:
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
        password_elem = browser.find_element_by_css_selector('#passwd')
        captcha_elem = browser.find_element_by_css_selector('#captchaCheck')
        captcha_img_elem = browser.find_element_by_css_selector('img[alt = "vtopCaptcha"]')
    except NoSuchElementException as err:
        print('Input elements with the given css selectors were not found: ' + err)
        sys.exit()

    #10. Find the image source of the captcha image
    captcha_img_src = captcha_img_elem.get_attribute('src')

    #11. Extract the base64 stribg of the captcha image from the captcha_img_src
    base64_img = captcha_img_src[22:]

    #12. Save the captcha image
    captcha_img = open('./captcha_save/captcha.png','wb')
    captcha_img.write(base64.b64decode(base64_img))
    captcha_img.close()

    #13. Convert the image into string
    img = Image.open('./captcha_save/captcha.png')
    captcha_str = CaptchaParse(img)

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
    try:
        WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.user-image')))
    except:
        print('Wrong registration number/password')
        sys.exit()

    #TODO: scrapped the profile to obtain different informations- time table of currrent day, for eg
    #14. Open the menu on the left using the toggle hamburger button- first find the button and then click
    try:
        waiting.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[role = "button"]')))
    except:
        print('VTOP taking too long to respond!')
        sys.exit()
    hamburger_elem = browser.find_element_by_css_selector('a[role = "button"]')
    hamburger_elem.click()

    #15. Find the Academics option in the left menu and lick on it
    academics_elem = browser.find_element_by_css_selector('#dbMenu ul.sidebar-menu.tree>li:nth-child(2)')
    academics_elem.click()

    #16. Get the time table element and click on it
    waiting.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#dbMenu ul.sidebar-menu.tree>li:nth-child(2) li:nth-child(2)>a span')))
    coursepage_elem = browser.find_element_by_css_selector('#dbMenu ul.sidebar-menu.tree>li:nth-child(2) li:nth-child(4)>a span')
    coursepage_elem.click()
    hamburger_elem.click()

    #17. Let the user select semester name and course from the page manually
    print('Choose Semester Name and Course from the dropdown on the page.')
    waiting.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.table')))

    js = '''
                window.filterTable = function() {
                    var faculty_name = document.getElementById('faculty').value
                    console.log("hahaha");
                    var all_rows = Array.prototype.slice.call(document.querySelectorAll('tbody tr'));
                    all_rows = all_rows.slice(1,);
                    console.log('hahahah2');

                    for(var i = 0; i < all_rows.length; i++) {
                        var all_tds = Array.prototype.slice.call(all_rows[i].querySelectorAll("td"));
                        var td_faculty_name = (all_tds[6].textContent.split(' - '))[1];

                        if(td_faculty_name.includes(faculty_name.toUpperCase())) {
                            console.log('hahahah3');
                            all_rows[i].style.display = "";
                            continue;
                        }
                        else {
                            console.log('hahaha4');
                            all_rows[i].style.display = "none";
                        }
                    };
                    document.body.setAttribute("faculty_name", faculty_name);
                }
                document.getElementById('getSlotIdForCoursePage').style.display = 'none';
                document.querySelector('#getFacultyForCoursePage label').outerHTML = '<font color= "red">' + document.querySelector('#getFacultyForCoursePage label').outerHTML + '</font>'

                var faculty_selector_parent = document.getElementById('faculty').parentNode
                faculty_selector_parent.innerHTML = "<input placeholder = 'Enter name of the faculty' onkeyup = 'filterTable()' class = 'form-control' id = 'faculty'>";

        '''

    browser.execute_script(js)

    js = '''
                window.filterTable = function() {
                    var faculty_name = document.getElementById('faculty').value;
                    console.log("hahaha");
                    var all_rows = Array.prototype.slice.call(document.querySelectorAll('tbody tr'));
                    all_rows = all_rows.slice(1,);
                    console.log('hahahah2');

                    for(var i = 0; i < all_rows.length; i++) {
                        var all_tds = Array.prototype.slice.call(all_rows[i].querySelectorAll("td"));
                        var td_faculty_name = (all_tds[6].textContent.split(' - '))[1];

                        if(td_faculty_name.includes(faculty_name.toUpperCase())) {
                            console.log('hahahah3');
                            all_rows[i].style.display = "";
                            continue;
                        }
                        else {
                            console.log('hahaha4');
                            all_rows[i].style.display = "none";
                        }
                    }
                    document.body.setAttribute("faculty_name", faculty_name);
                };

            document.getElementById('courseCode').onchange = function() {
                            getSlotIdForCoursePage('courseCode','getSlotIdForCoursePage','source');
                            setTimeout(function() {
                                    document.getElementById('getSlotIdForCoursePage').style.display = 'none';
                                    document.querySelector('#getFacultyForCoursePage label').outerHTML = '<font color= "red">' + document.querySelector('#getFacultyForCoursePage label').outerHTML + '</font>';
                                    var faculty_selector_parent = document.getElementById('faculty').parentNode;
                                    faculty_selector_parent.innerHTML = "<input placeholder = 'Enter name of the faculty' onkeyup = 'filterTable()' class = 'form-control' id = 'faculty'>";
                            }, 3500);
                        };
            '''

    while True:
        browser.execute_script(js)
        find_download_element()

except NoSuchWindowException:
    print('Either the browser is closed or the Authorization failed! Do comeback!')
