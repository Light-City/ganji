

![](http://p20tr36iw.bkt.clouddn.com/ganji_page.jpg)

<!--more-->

# 告别裸奔，赶集抓手



## 1.告别裸奔

【**裸奔**】

在爬虫过程中，有时有些网站具有反爬虫设置，当爬取次数到达一定程度，那么这个网站就会禁止你的IP对其进行访问，这就是裸奔操作，为了不让对方服务器发现你在爬取对面的网站信息。

换句话说，以隐藏身份爬取对应网站，那么这里就采取从西刺网站爬取国内高匿代理IP设置代理参数，从而隐藏自己，接下来先来看一下，如何实现西刺ip的爬取及处理呢？

西刺代理：`http://www.xicidaili.com/nn`

【**分析**】

![](http://p20tr36iw.bkt.clouddn.com/xici.png)

在上图中，三个红色框，分别表示，ip，端口，以及类型，最终所要实现的结果是：`{'HTTP':'HTTP://ip:port'}`

这里我只是利用西刺的数据，去爬取赶集网数据。所以这里只选择了4页数据进行处理，如果想要更多数据，去建立一个自己的代理池，那么只需要变动循环次数，或者获取下一页的url即可进行多页面获取！

【**代码**】

```python
baseurl = 'http://www.xicidaili.com/nn/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}
http_list = []
def get_IP():
    print('-----IP爬取进度-----')
    # 只爬取4页的ip
    for i in range(1,5):
        print('------第' + str(i) + '页开始爬取------')
        url = baseurl + str(i)
        raw_html = requests.get(url, headers=headers).text
        # print(raw_html)
        selector = etree.HTML(raw_html)
        # td[index]中index从1开始,分别获取ip,port,type
        ip = selector.xpath('//tr[@class="odd"]//td[2]/text()') 
        port = selector.xpath('//tr[@class="odd"]//td[3]/text()')
        httptype = selector.xpath('//tr[@class="odd"]//td[6]/text()')
        # 上述ip/port/type均为list数据(存储的是当页数据)，我们需要将其每一个数据转换为{'HTTP':'HTTP://ip:port'}格式，用在requests.get里面的proxies参数里面！
        for eachip,eachport,eachtype in zip(ip,port,httptype):
            http_dict = {}
            http_dict[eachtype] = eachtype + '://' + eachip + ':' + eachport
            http_list.append(http_dict)
        print(http_list) # 两页总共的ip
        print('------第' + str(i) + '页爬取结束------')
        
    # 返回的数据格式为[{},{},{}.....]
    return http_list
print('------IP爬虫结束------')
```

【**数据**】

![](http://p20tr36iw.bkt.clouddn.com/py_iptotal.png)

## 2.赶集抓手

【**分析**】

本次主要想获取赶集网二手房信息，如下列字段：

![](http://p20tr36iw.bkt.clouddn.com/ziduan_ganji.png)

在分析中发现两个问题：

**第一：**网站反爬虫处理，当访问次数过多，就会有验证操作，如下图即为当前验证操作的源码。

![](http://p20tr36iw.bkt.clouddn.com/ganjia_code.png)

**第二：**我们直观看到只有10个页面，但是当你点击第10个页面(如下图)的时候会发现,后面又有新的页面(如下图)了，于是这里就不能直接通过获取页面总个数，进行遍历，那么该如何操作呢？

对于多页面的处理除了上述，还有两种，第一：模拟js或者触发相应事件；第二：直接获取下一页的url，进行拼接即可。从上述方法中，我选择了第二种，那么这个多页面问题就又解决了。

以下分别为打开赶集首页以及点击第10页后的页面！

![](http://p20tr36iw.bkt.clouddn.com/py_ganji.png)

![](http://p20tr36iw.bkt.clouddn.com/page_ganji.png)

【**功能**】

- 西刺IP本地存储及读取
- 通过西刺IP爬页面
- 数据提取
- 美化打印
- 数据库存储(包括mysql及mongodb)

这里先给大家看一下，最后的运行结果，有个直观的感受。

![](http://p20tr36iw.bkt.clouddn.com/ganji_mongodb.png)

![](http://p20tr36iw.bkt.clouddn.com/py_ganjia_mysql.png)

当前为第5页数据，有368条，前4个页面，每页1000条，那么总共4368条，同上面的mongodb一致！

![](http://p20tr36iw.bkt.clouddn.com/py_ganji_csv.png)

mysql导出数据表，共4369行，减掉第一行的字段，共4368行。

![](http://p20tr36iw.bkt.clouddn.com/py_ganji_1.png)

【**实现**】

- 封装

```python
MONGO_URI = 'localhost'
MONGO_DB = 'test' # 定义数据库
MONGO_COLLECTION = 'ganji' # 定义数据库表
class ganji_spider(object):
    def __init__(self,mongo_uri,mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
```

- 获取源码

```python
def get_html(self, url, proxies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    raw_html = requests.get(url, headers=headers, proxies=proxies).text
    return raw_html
```

- 西刺IP存储

```python

def save_proxies(self, http_list):
    ouf = open("valid_ip.txt", "a+")
    for each_proxies in http_list:
        ouf.write(str(each_proxies))
        ouf.write('\n')
```

- 随机行读取上述存储的IP(每一行代表一个proxies)，利用代理爬取网页

```python
def avoid_verifi(self, http_list, url):
    # print(http_list)
    # print(len(http_list))
    while True:
        random_line = random.randint(1, len(http_list))
        theline = open('valid_ip.txt', 'r').readlines()[random_line]
        theline = theline.replace("'", '"')  # 单引号全部替换为双引号
        theline = json.loads(theline)  # str转dict(字典)格式
        print("正在使用的代理IP：" + str(theline))
        try:
            html = self.get_html(url, theline)
            # print(html)
            if "访问过于频繁，本次访问做以下验证码校验" not in html:
                return html
        except Exception as e:
            print('.....')
```

- 数据提取

下面异常处理的目的是防止缺失字段，对缺失字段处理！

```python
def get_AllPage(self, url):
    raw_html = self.avoid_verifi(http_list, url)
    selector = etree.HTML(raw_html)
    try:
        # 房子名称
        hose_title = selector.xpath('//dd[@class="dd-item title"]//a/text()')
    except Exception as e:
        hose_title = 0
        print('房名error!')
    try:
        # 房子价格
        hose_price = selector.xpath(
            '//dd[@class="dd-item info"]//div[@class="price"]/span[@class="num js-price"]/text()')
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
            # 去掉换行及空格
            each_site = each_site.replace('\n', '').replace(' ', '')
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
    return hose_title, hose_price, hose_eachprice, house_type, house_site, hose_size
```

- 数据库存储

下面存储包含两大存储：mongodb与mysql

```python
def Save_DB(self, hose_title, hose_price, hose_eachprice, house_type, house_site, hose_size):
    for htitle, hprice, hpr, htype, hsite, hsize in zip(hose_title, hose_price, hose_eachprice, house_type, house_site,
                                                        hose_size):
        data = {}
        data['房子名称'] = htitle
        data['房子价格'] = hprice
        data['房子单价'] = hpr
        data['房子类型'] = htype
        data['房子地址'] = hsite
        data['房子大小'] = hsize
        # mongodb存储
        self.db[MONGO_COLLECTION].insert_one(data)
        self.client.close()
        # mysql存储
        connection = pymysql.connect(host='localhost', user='root', password='xxxx', db='scrapydb',
                                     charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                sql = "insert into `ganji`(`房子名称`,`房子价格`,`房子单价`,`房子类型`,`房子地址`,`房子大小`)values(%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (htitle, hprice, hpr, htype, hsite, hsize))
            connection.commit()
        finally:
            connection.close()
```

【调用】

```python
if __name__ == '__main__':
    # 类初始化
    ganji = ganji_spider(MONGO_URI,MONGO_DB)
    # 调用西刺IP
    http_list = get_IP()
    # 存储IP
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
        # 代理获取真实的html
        raw_html = ganji.avoid_verifi(http_list,pagedict[str(page_number)])
        selector = etree.HTML(raw_html)

        hose_title, hose_price, hose_eachprice, house_type, house_site, hose_size = ganji.get_AllPage(pagedict[str(page_number)])
        # PrettyTable格式化打印
        tb = pt()
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
        # 计算数据存储耗时
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
```







































