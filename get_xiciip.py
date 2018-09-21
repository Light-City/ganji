
import requests
from lxml import etree

import json
import random
baseurl = 'http://www.xicidaili.com/nn/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

http_list = []

def get_IP():
    print('-----IP爬取进度-----')
    for i in range(1,5):
        print('------第' + str(i) + '页开始爬取------')
        url = baseurl + str(i)
        raw_html = requests.get(url, headers=headers).text
        # print(raw_html)
        selector = etree.HTML(raw_html)
        # td[index]中index从1开始
        ip = selector.xpath('//tr[@class="odd"]//td[2]/text()')
        port = selector.xpath('//tr[@class="odd"]//td[3]/text()')
        httptype = selector.xpath('//tr[@class="odd"]//td[6]/text()')
        for eachip,eachport,eachtype in zip(ip,port,httptype):
            http_dict = {}
            http_dict[eachtype] = eachtype + '://' + eachip + ':' + eachport
            http_list.append(http_dict)
        print(http_list) # 两页总共的ip
        print('------第' + str(i) + '页爬取结束------')
    return http_list

print('------IP爬虫结束------')

# 用于测试
if __name__ == '__main__':
    http_list = get_IP()
    print(http_list)
    print(len(http_list))

    ouf = open("valid_ip.txt", "a+")

    # 分行存储
    for each_proxies in http_list:
        ouf.write(str(each_proxies))
        ouf.write('\n')

    a = random.randint(1, len(http_list))
    # 分行随机读取
    theline = open('valid_ip.txt', 'r').readlines()[a]
    print('------------------------')
    print(theline)

    theline = theline.replace("'", '"')
    theline = json.loads(theline)
    print(theline)
    print(type(theline))
    html = requests.get('http://cq.ganji.com/fang5/o5/', headers=headers, proxies=theline).text
    print(html)


