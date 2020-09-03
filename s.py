# coding: utf-8

from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Thread,Lock
import os
import csv
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
import re

# 下面是利用 selenium 抓取html页面的代码

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)#options=chrome_options
url_list = []

def get_url():

    print('正在获取货币基金排行榜......')
    #
    driver.get('http://fund.eastmoney.com/data/hbxfundranking.html')
    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#dbtable')))
    html = driver.page_source
    doc = pq(html)
    items = doc('#dbtable > tbody > tr > td:nth-child(3) > a').items()

    for i in items:
        url = 'http://fundf10.eastmoney.com/jjjz_{}.html'.format(i.text())
        # print(url)
        url_list.append(url)

    # get_next_url()














    # return url_list

# def get_next_url():
#     for i in range(2,4):
#
#
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#dbtable > tbody')))
#         inputs = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, '#pnum')))
#         submit = WebDriverWait(driver, 20).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, '#pagebar > input.pgo')))
#
#         inputs.clear()  # 第x页 输入框
#         inputs.send_keys(str(i))  # 去第x页
#         submit.click()  # 点击按钮
#
#         html = driver.page_source
#         doc = pq(html)
#         items = doc('#dbtable > tbody > tr > td:nth-child(3) > a').items()
#         for i in items:
#             url = 'http://fundf10.eastmoney.com/jjjz_{}.html'.format(i.text())
#             # print(url)
#             url_list.append(url)
#



# 初始化函数
def initSpider(url):

    # driver = webdriver.Chrome()
    driver.get(url) # 要抓取的网页地址

    # 找到"下一页"按钮,就可以得到它前面的一个label,就是总页数
    getPage_text = driver.find_element_by_id("pagebar").find_element_by_xpath(
        "div[@class='pagebtns']/label[text()='下一页']/preceding-sibling::label[1]").get_attribute("innerHTML")
    # 得到总共有多少页
    total_page = int("".join(filter(str.isdigit, getPage_text)))

    # 返回
    return total_page

# 获取html内容
def getData(myrange,lock):

    for x in myrange:
        # 锁住
        lock.acquire()

        tonum = driver.find_element_by_id("pagebar").find_element_by_xpath(
            "div[@class='pagebtns']/input[@class='pnum']")  # 得到 页码文本框
        jumpbtn = driver.find_element_by_id("pagebar").find_element_by_xpath(
            "div[@class='pagebtns']/input[@class='pgo']")  # 跳转到按钮

        tonum.clear()  # 第x页 输入框
        tonum.send_keys(str(x))  # 去第x页
        jumpbtn.click()  # 点击按钮

        # 抓取
        # WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id("pagebar").find_element_by_xpath("div[@class='pagebtns']/label[@value={0} and @class='cur']".format(x)) != None)


        ################################





        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#jztable > table > tbody')))
        html = driver.page_source
        doc = pq(html)
        #items_name = doc('#jztable > table > thead > tr > th').items()
        items = doc('#jztable > table > tbody > tr').items()

        filename = doc('#bodydiv > div:nth-child(13) > div.r_cont.right > div.basic-new > div.bs_jz > div.col-left > h4 > a').text()
        if 'fund_csv' not in os.listdir():
            os.makedirs('fund_csv')
        if x == 1:
            header = ['净值日期','每万份收益','7日年化收益率（%）']
            with open("./fund_csv/{}.csv".format(filename), 'a',newline='',encoding='gbk') as f:
                write = csv.writer(f)
                write.writerow(header)
                f.close()

        with open("./fund_csv/{}.csv".format(filename), 'a', newline='',encoding='gbk') as f:

            for item in items:

                fund = [
                    item.find('td:nth-child(1)').text().strip(),
                    re.compile('((-?\d+)(\.\d+)?)').search(item.find('td:nth-child(2)').text().strip()).group(1),
                    item.find('td:nth-child(3)').text(),
                ]
                # fund = {
                #     'date':item.find('td:nth-child(1)').text() ,
                #     'net_unit':item.find('td:nth-child(2)').text().strip(),
                #     'accumulated_net':item.find('td:nth-child(3)').text(),
                #     'rate':item.find('td:nth-child(4)').text(),
                #     'requisition_status':item.find('td:nth-child(5)').text(),
                #     'redemption_status':item.find('td:nth-child(6)').text()
                # }


                # print(fund)
                # 保存到项目中
                # with open("./fund_csv/{}.csv".format(filename), 'a',encoding='utf-8',  newline=None) as f:
                write = csv.writer(f)
                write.writerow(fund)
            f.close()
            ################################



        # 解锁
        lock.release()






# 开始抓取函数
def beginSpider(url):
    # 初始化爬虫
    total_page = initSpider(url)
    # 创建锁
    lock = Lock()

    r = range(1, int(total_page)+1)
    step = 10
    range_list = [r[x:x + step] for x in  range(0, len(r), step)]   #把页码分段
    thread_list = []
    for r in  range_list:
        t = Thread(target=getData, args=(r,lock))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join() # 这一步是需要的,等待线程全部执行完成

    print("抓取{}完成".format(url))

def main():
    get_url()
    # count = 0
    for url in url_list:
        # count += 1
        beginSpider(url)
    driver.close()


if __name__ == '__main__':
    main()