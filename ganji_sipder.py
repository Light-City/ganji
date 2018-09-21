import random
import json
import time
from prettytable import PrettyTable as pt
import pymysql
import requests
import pymongo
from get_xiciip import get_IP
from lxml import etree
MONGO_URI = 'localhost'
MONGO_DB = 'test' # 定义数据库
MONGO_COLLECTION = 'ganji' # 定义数据库表
class ganji_spider(object):
    def __init__(self,mongo_uri,mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    def get_html(self,url,proxies):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        raw_html = requests.get(url,headers=headers,proxies=proxies).text
        return raw_html

    def save_proxies(self,http_list):
        ouf = open("valid_ip.txt", "a+")
        for each_proxies in http_list:
            ouf.write(str(each_proxies))
            ouf.write('\n')

    def avoid_verifi(self,http_list,url):
        # print(http_list)
        # print(len(http_list))
        while True:
            random_line = random.randint(1, len(http_list))
            theline = open('valid_ip.txt', 'r').readlines()[random_line]
            theline = theline.replace("'", '"') # 单引号全部替换为双引号
            theline = json.loads(theline) # str转dict(字典)格式
            print("正在使用的代理IP：" + str(theline))
            try:
                html = self.get_html(url,theline)
                # print(html)
                if "访问过于频繁，本次访问做以下验证码校验" not in html:
                    return html
            except Exception as e:
                print('.....')



    def get_AllPage(self,url):
        raw_html = self.avoid_verifi(http_list,url)
        selector = etree.HTML(raw_html)
        try:
            # 房子名称
            hose_title = selector.xpath('//dd[@class="dd-item title"]//a/text()')
        except Exception as e:
            hose_title = 0
            print('房名error!')
        try:
            # 房子价格
            hose_price = selector.xpath('//dd[@class="dd-item info"]//div[@class="price"]/span[@class="num js-price"]/text()')
        except Exception as e:
            hose_price = '0'
            print('房价error!')
        try:
            # 房子单价
            hose_eachprice = selector.xpath('//dd[@class="dd-item info"]//div[@class="time"]/text()')
        except Exception as e:
            hose_eachprice = '0'
            print('单价error!')
        try:
            # 房子户型
            house_type = selector.xpath('//dd[@class="dd-item size"]//span[@class="first js-huxing"]/text()')
        except Exception as e:
            house_type = '0'
            print('户型error!')
        try:
            # 房子地址
            span_list = selector.xpath('//dd[@class="dd-item address"]//span')
            house_site = []
            for each_span in span_list:
                # string(.) 标签套标签
                each_site = each_span.xpath('string(.)')
                each_site = each_site.replace('\n','').replace(' ','')
                house_site.append(each_site)
        except Exception as e:
            house_site = '0'
            print('地址error!')
        try:
            # 房子大小
            hose_size = selector.xpath('//dd[@class="dd-item size"]/span[3]/text()')
        except Exception as e:
            hose_size = '0'
            print('大小error!')
        return hose_title,hose_price,hose_eachprice,house_type,house_site,hose_size

    def Save_DB(self,hose_title,hose_price,hose_eachprice,house_type,house_site,hose_size):
        for htitle,hprice,hpr,htype,hsite,hsize in zip(hose_title,hose_price,hose_eachprice,house_type,house_site,hose_size):
            data = {}
            data['房子名称'] = htitle
            data['房子价格'] = hprice
            data['房子单价'] = hpr
            data['房子类型'] = htype
            data['房子地址'] = hsite
            data['房子大小'] = hsize
            self.db[MONGO_COLLECTION].insert_one(data)
            self.client.close()
            connection = pymysql.connect(host='localhost', user='root', password='xxxx', db='scrapydb',
                                         charset='utf8mb4')
            try:
                with connection.cursor() as cursor:
                    sql = "insert into `ganji`(`房子名称`,`房子价格`,`房子单价`,`房子类型`,`房子地址`,`房子大小`)values(%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (htitle, hprice, hpr, htype, hsite, hsize))
                connection.commit()
            finally:
                connection.close()


if __name__ == '__main__':
    ganji = ganji_spider(MONGO_URI,MONGO_DB)
    http_list = get_IP()
    ganji.save_proxies(http_list)
    page_number = 1
    index = 1
    pagedict = {}
    while True:
        print("-----第" + str(page_number) + "页爬取开始------")
        ganji_data = {}
        baseurl = 'http://cq.ganji.com'
        if page_number==1:
            page_link = baseurl + '/fang5/o1/'
            pagedict[str(page_number)] = page_link
        raw_html = ganji.avoid_verifi(http_list,pagedict[str(page_number)])
        selector = etree.HTML(raw_html)

        hose_title, hose_price, hose_eachprice, house_type, house_site, hose_size = ganji.get_AllPage(pagedict[str(page_number)])
        tb = pt()
        # PrettyTable格式化打印
        tb.add_column('房子名称',hose_title)
        tb.add_column('房子价格',hose_price)
        tb.add_column('房子单价',hose_eachprice)
        tb.add_column('房子类型',house_type)
        tb.add_column('房子地址',house_site)
        tb.add_column('房子大小',hose_size)
        print(tb)
        t1 = time.time()
        ganji.Save_DB(hose_title, hose_price, hose_eachprice, house_type, house_site, hose_size)
        t = time.time() - t1
        print('存储耗时：' + str(t))
        try:
            page_nextText = selector.xpath('//ul[@class="pageLink clearfix"]//li//a[@class="next"]/span/text()')[0]
            print(page_nextText)
        except Exception as e:
            # 避免到最后一页报错！
            break
            print('爬虫完毕！')
        page_nextUrl = selector.xpath('//ul[@class="pageLink clearfix"]//li//a[@class="next"]/@href')[0]

        print(page_nextUrl)
        if page_nextText == '下一页 >':
            index += 1
            print(index)
            pagedict[str(index)] = baseurl + page_nextUrl
            print(pagedict)
            print("-----第" + str(page_number) + "页爬取结束,5秒后重抓------")
        else:
            print("-----第" + str(page_number) + "是最后一页，没有下一页，爬虫结束---")
            break

        page_number += 1
        print(page_number)
        # time.sleep(5) 没有代理ip,需要加上此行！

    print("------爬虫全部结束------")



