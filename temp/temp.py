import requests
from selenium import webdriver

browser = webdriver.Firefox()

browser.get('http://vtop.vit.ac.in')

try:
    vtopbeta_elem = browser.find_element_by_css_selector('a[href = "https://vtopbeta.vit.ac.in/vtop"] font b')
    print('Found element that href\'s to vtopbeta')
except:
    print('No element with attribute value a[href="https://vtopbeta.vit.ac.in/vtop"] was found')

browser.get(vtopbeta_elem.text)


browser.quit()
