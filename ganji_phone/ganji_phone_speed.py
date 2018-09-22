import random

from lxml import etree
import requests
import json
from urllib import parse
import re
from prettytable import PrettyTable as pt

from get_xiciip import get_IP


class phone_spider(object):
    def __init__(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        http_list = get_IP()
        self.url = url
        self.headers = headers
        self.http_list = http_list
    def save_proxies(self):
        ouf = open("valid_ip.txt", "a+")
        for each_proxies in self.http_list:
            ouf.write(str(each_proxies))
            ouf.write('\n')
    def url_Process(self):
        # 从http://cq.ganji.com/fang5/3552816612x.htm中提取处http://cq.ganji.com/
        url_head = re.findall(r'(.+.com/)', self.url)[0]
        return url_head

    def get_html(self):
        while True:
            random_line = random.randint(1, len(self.http_list))
            theline = open('valid_ip.txt', 'r').readlines()[random_line]
            theline = theline.replace("'", '"')  # 单引号全部替换为双引号
            theline = json.loads(theline)  # str转dict(字典)格式
            print("正在使用的代理IP：" + str(theline))
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                }
                html = requests.get(self.url, headers=headers, proxies=theline).text
                # print(html)
                if "访问过于频繁，本次访问做以下验证码校验" not in html:
                    return html,theline # # 返回源码及代理
            except Exception as e:
                print('.....')
    def get_Info(self):
        raw_html,proxies = self.get_html()
        selector = etree.HTML(raw_html)
        phone = selector.xpath('//div[@id="full_phone_show"]/@data-phone')[0]
        puid = selector.xpath('//input[@id="puid"]/@value')[0]
        user_id = selector.xpath('//input[@id="user_id_hide"]/@value')[0]
        name = selector.xpath('//div[@class="name"]/text()')[0]
        # 去掉name的回车换行及空格
        name = name.replace('\n','').replace(' ','')
        return phone,puid,user_id,name

    def encode_Phone(self):
        phone, puid, user_id, name = self.get_Info()
        # phone转为字典
        dict_phone = {}
        dict_phone["phone"] = phone
        # 传递字典phone
        encode_phone = parse.urlencode(dict_phone)
        return encode_phone
    def get_Phone(self):
        raw_html, proxies = self.get_html()
        phone, puid, user_id, name = self.get_Info()
        url_head = self.url_Process()
        encode_phone = self.encode_Phone()
        par_url = url_head + 'ajax.php?dir=house&module=secret_phone&user_id=' + user_id + '&puid=' + puid + '&major_index=5' + '&' + encode_phone + '&isPrivate=1'
        raw_data = requests.get(par_url, headers=self.headers, proxies=proxies).text
        return raw_data
    def phone_Extract(self):
        raw_data = self.get_Phone()
        data= json.loads(raw_data)
        return data["secret_phone"]

if __name__ == '__main__':
    url = 'http://cq.ganji.com/fang5/3552816612x.htm'
    ps = phone_spider(url)
    ps.save_proxies()
    raw_phone, puid, user_id, name= ps.get_Info()
    print("----------请求关键参数如下----------")
    table = pt(["raw_phone","puid","user_id"])
    table.add_row([raw_phone,puid,user_id])
    print(table)
    phone = ps.phone_Extract()
    print(name + '的联系电话为' + phone)


