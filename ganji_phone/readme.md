
![](http://p20tr36iw.bkt.clouddn.com/ganji_phone.jpg)

<!--more-->

# 揭开神秘的面纱

## 0.说在前面

**两种方式**实现抓取**ajax动态电话号码 **：

- 第一种：selenium + chromdriver实现

- 第二种：获取参数，拼接请求

## 1.爬虫思想

打开f12检查页面后，刷新一下页面，点击Network，再点击下面的XHR，查看动态数据，会发现如下图所示，有两行数据。

![](http://p20tr36iw.bkt.clouddn.com/ganji_phonexhr.png)

当我们点击查看电话时，会发现如下图所示，多了一行数据，那么接下来我们来点一下这个数据，查看详情！

![](http://p20tr36iw.bkt.clouddn.com/ganji_phone_true.png)

首先查看一下Headers里面的关键信息，如下面两图所示：

![](http://p20tr36iw.bkt.clouddn.com/guazi_req.png)

![](http://p20tr36iw.bkt.clouddn.com/guazi_param.png)

在上图的Query String Parameters处点击同行的view URL encoded，会发现跟图1的Request URL一致。也就是说只我们按照图1的get方式请求对应的URL，应该即可获取到相应的数据，事实确实如此，就这么简单！

但是呢，每一个页面都有那些参数，难道我们每爬取一个页面就得重新改这些参数或者这么长的url？岂不是太复杂了，那么现在我们对其进行智能化处理。下图为我们获取的数据格式，只需要获得secret_phont对应的value即可！

![](http://p20tr36iw.bkt.clouddn.com/phone_res.png)

那么我们来看一下未点击查看电话时候的源码，并从中获取以上的参数即可。在获取参数之前，自己去尝试几个不同的页面会发现，只有user_id、puid以及phone参数对应的值不一样，那么只需要获取这几个就可以了。

如下图为关键参数phone的页面(其余2个参数类似，就不展开说明了)：

![](http://p20tr36iw.bkt.clouddn.com/ganji_phone_anl.png)

## 2.selenium + chromdriver实现

【类封装】

```python
class selenium_spider(object):
    def __init__(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        self.url = url
        http_list = get_IP()
        self.headers = headers
        self.http_list = http_list
```

【存储代理】

```python
def save_proxies(self):
    ouf = open("valid_ip.txt", "a+")
    for each_proxies in self.http_list:
        ouf.write(str(each_proxies))
        ouf.write('\n')
```

【获取代理】

```python
def avoid_verifi(self,url):
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
                    print(key) # key即为HTTP或HTTPS
                    print(value) 
                    return value # value即为HTTP://ip:port或者HTTPS://ip:port形式
        except Exception as e:
            print('.....')
```

【selenium实现】

```python
def selnium_clawl(self,proxies):
    proxies = re.findall('(//.*)', proxies)[0]
    print(proxies)
    print(proxies.replace('//', '')) # http://ip:port提取处ip:port
    chromeOptions = webdriver.ChromeOptions()
    # 设置代理
    chromeOptions.add_argument('--proxy-server={0}'.format(proxies))
    driver = webdriver.Chrome(chrome_options=chromeOptions)
    driver.implicitly_wait(5)  # seconds
    driver.get(self.url)
    raw_phone = driver.find_element_by_xpath("//a[@class='phone_num js_person_phone']")
    raw_phone.click()
    time.sleep(5)  # 等待10s
    print(raw_phone.text)
```

注意：以上是添加代理后的代码，有可能因为代理问题无法正常爬取，只需要去掉代理便可以。

## 3.获取参数，拼接请求

【封装】

```python
class phone_spider(object):
    def __init__(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        http_list = get_IP()
        self.url = url
        self.headers = headers
        # [{},{}...]形式的代理
        self.http_list = http_list
```

【代理存储】

```python
def save_proxies(self):
    ouf = open("valid_ip.txt", "a+")
    for each_proxies in self.http_list:
        ouf.write(str(each_proxies))
        ouf.write('\n')
```

【获取源码及代理】

```python
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
                return html,theline # 
        except Exception as e:
            print('.....')
```

【数据提取】

```python
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
```

【获取编码后的phone】

```python
def encode_Phone(self):
    phone, puid, user_id, name = self.get_Info()
    # phone转为字典
    dict_phone = {}
    dict_phone["phone"] = phone
    # 传递字典phone
    encode_phone = parse.urlencode(dict_phone)
    return encode_phone
```

【获取请求的url前缀】

```python
def url_Process(self):
    # 从http://cq.ganji.com/fang5/3552816612x.htm中提取处http://cq.ganji.com/
    url_head = re.findall(r'(.+.com/)', self.url)[0]
    return url_head
```

【参数拼接，发送请求】

```python
def get_Phone(self):
    raw_html, proxies = self.get_html()
    phone, puid, user_id, name = self.get_Info()
    url_head = self.url_Process()
    encode_phone = self.encode_Phone()
    par_url = url_head + 'ajax.php?dir=house&module=secret_phone&user_id=' + user_id + '&puid=' + puid + '&major_index=5' + '&' + encode_phone + '&isPrivate=1'
    raw_data = requests.get(par_url, headers=self.headers, proxies=proxies).text
    return raw_data
```

【提取电话号码】

```python
def phone_Extract(self):
    raw_data = self.get_Phone()
    data= json.loads(raw_data)
    return data["secret_phone"]
```

【类调用】

```python
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
```

【结果呈现】

![](http://p20tr36iw.bkt.clouddn.com/ganji_phone.png)





