import requests
from lxml import etree
import os

def getUrl_list(url):
    print('开始获取网页列表链接')
    r = requests.get(url)
    html = etree.HTML(r.content, parser=etree.HTMLParser())
    # html = etree.parse('4kbian网.html',parser=etree.HTMLParser())
    num = int(html.xpath('//span[@class="slh"]/following::*/text()')[0])
    url_list = []
    start_url = 'http://pic.netbian.com/4kdongman/'
    url_list.append(start_url)
    for i in range(2, num + 1):
        url = (start_url + 'index_' + str(i) + '.html')
        url_list.append(url)
    print('获取网页列表链接成功')
    return url_list

def getImg_list(url_list):
    print('开始获取图片列表链接')
    img_list = []
    for i in url_list:
        r = requests.get(i)
        html = etree.HTML(r.content, parser=etree.HTMLParser())
        img_url = html.xpath('//div[@class="slist"]//a[@target="_blank"]/@href')
        for j in img_url:
            img_list.append("http://pic.netbian.com"+j)
    print('获取图片列表链接成功')
    return img_list

def downloadImges(img_list):
    print('开始下载图片')
    path = './images/'
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    for i in img_list:
        r = requests.get(i)
        html = etree.HTML(r.content, parser=etree.HTMLParser())
        img_url = "http://pic.netbian.com" + html.xpath('//div[@class="photo-pic"]/a[@id="img"]/img/@src')[0]
        t = html.xpath('//div[@class="photo-hd"]/h1/text()')[0]
        title = t.strip()
        image = requests.get(img_url)
        name = path+title+'.jpg'
        with open(name,'wb') as f:
            f.write(image.content)
            print(title+'.jpg下载成功')
    f.close()

if __name__ == '__main__':
    url = 'http://pic.netbian.com/4kdongman/'
    url_list = getUrl_list(url)
    img_list = getImg_list(url_list)
    downloadImges(img_list)  
