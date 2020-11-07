import requests 
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time

firefoxOptions = Options()

firefoxOptions.add_argument('-headless')

url='https://www.realosophy.com/east-york-former-toronto/neighbourhood-map?neighbourhood=central-east-york-toronto'

driver = webdriver.Firefox(options=firefoxOptions)
driver.get(url)

time.sleep(5)

html= driver.page_source

soup = BeautifulSoup(html,'lxml')
all_divs = soup.find('div',{'class':'neighbourhood-map__avg-sale-price ng-binding ng-scope'})

print(all_divs.text)

driver.quit()
