
from selenium import webdriver

# 获取动态的联系电话
url = 'http://cq.ganji.com/fang5/3552816612x.htm'

driver = webdriver.Chrome()
driver.implicitly_wait(10) # seconds
driver.get(url)


raw_phone = driver.find_element_by_xpath("//a[@class='phone_num js_person_phone']")
raw_phone.click()
import  time
time.sleep(10) # 等待10s
html = driver.page_source
print(raw_phone.text)
