import json

import requests
from selenium import webdriver
import time
from get_xiciip import get_IP
import random
import re
class selenium_spider(object):
    def __init__(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        self.url = url
        http_list = get_IP()
        self.headers = headers
        self.http_list = http_list

    def avoid_verifi(self, url):
        # print(http_list)
        # print(len(http_list))
        while True:
            random_line = random.randint(1, len(self.http_list))
            theline = open('valid_ip.txt', 'r').readlines()[random_line]
            theline = theline.replace("'", '"')  # 单引号全部替换为双引号
            theline = json.loads(theline)  # str转dict(字典)格式
            print("正在使用的代理IP：" + str(theline))
            try:

                html = requests.get(url, headers=self.headers, proxies=theline).text
                # print(html)
                if "访问过于频繁，本次访问做以下验证码校验" not in html:
                    for key, value in theline.items():
                        print(key)  # key即为HTTP或HTTPS
                        print(value)
                        return value  # value即为HTTP://ip:port或者HTTPS://ip:port形式
            except Exception as e:
                print('.....')
    def save_proxies(self):
        ouf = open("valid_ip.txt", "a+")
        for each_proxies in self.http_list:
            ouf.write(str(each_proxies))
            ouf.write('\n')

    def selnium_clawl(self,proxies):

        proxies = re.findall('(//.*)', proxies)[0]
        print(proxies)
        print(proxies.replace('//', ''))
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--proxy-server={0}'.format(proxies))
        driver = webdriver.Chrome(chrome_options=chromeOptions)
        driver.implicitly_wait(5)  # seconds
        driver.get(self.url)
        raw_phone = driver.find_element_by_xpath("//a[@class='phone_num js_person_phone']")
        raw_phone.click()
        time.sleep(5)  # 等待10s
        print(raw_phone.text)

# 获取动态的联系电话
if __name__ == '__main__':
    url = 'http://cq.ganji.com/fang5/3552816612x.htm'
    sp = selenium_spider(url)
    proxies = sp.avoid_verifi(url)
    print("---------主程序---------")
    print("选用的最终代理为：" + proxies)
    sp.selnium_clawl(proxies)



