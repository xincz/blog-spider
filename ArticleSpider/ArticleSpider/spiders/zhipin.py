# coding: utf-8

import os
import time
import pickle
import scrapy
from datetime import datetime
from selenium import webdriver
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from items import GeneralJobItemLoader, GeneralJobItem
from utils.common import get_md5
from settings import BASE_DIR



class ZhipinSpider(CrawlSpider):
    name = 'zhipin'
    allowed_domains = ['www.zhipin.com']
    start_urls = ['https://www.zhipin.com/job_detail/a02d21421ad2a24d0Xx43tq8EVI~.html']
    # start_urls = ['http://www.zhipin.com/']

    rules = (
        Rule(LinkExtractor(allow=('gongsi/.*',)), follow=True),
        Rule(LinkExtractor(allow=('gongsir/.*.html',)), follow=True),
        Rule(LinkExtractor(allow=r'job_detail/.*~.html'), callback='parse_job', follow=True),
    )

    # 反反爬
    cookies = {
        "__zp_stoken__": "bf79ElaZ4z7IK5JruWAX5j256l7CJf3k7Ag2A9mrsSPN%2FnLgjChK0LguCrB%2FtIEFMKdnysNhr4ilqIicjeHkCsCpBQ%3D%3D"
    }  # 设置cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Referer': 'https://www.zhipin.com/web/common/security-check.html?seed=6gkgYHovIokVntQcwXUH9KW3%2FbEZsqfeaoCctIp1rE8%3D&name=f2d51032&ts=1571623520634&callbackUrl=%2Fjob_detail%2F%3Fquery%3D%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%26city%3D100010000%26industry%3D%26position%3D&srcReferer=https%3A%2F%2Fwww.zhipin.com%2Fjob_detail%2F%3Fquery%3D%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%26city%3D100010000%26industry%3D%26position%3D'
    }  # 设置登录头

    # 爬虫的入口点，重载此方法
    def start_requests(self):
        # Load Cookies
        cookies = []
        if os.path.exists(BASE_DIR + '/cookies/zhipin.cookie'):
            cookies = pickle.load(open(BASE_DIR + '/cookies/zhipin.cookie', 'rb'))

        if not cookies:
            # Selenium simulate login
            browser = webdriver.Chrome(executable_path="C:/Users/ace01/Downloads/browser_drivers/chromedriver.exe")
            browser.get("https://www.zhipin.com/user/login.html")
            browser.find_element_by_css_selector(".ipt-wrap .ipt-phone").send_keys("")
            browser.find_element_by_css_selector(".ipt-wrap .ipt-pwd").send_keys("")
            browser.find_element_by_css_selector('.geetest_radar_tip').click()
            time.sleep(10)
            browser.find_element_by_css_selector('.form-btn .btn').click()
            time.sleep(5)

            cookies = browser.get_cookies()
            pickle.dump(cookies, open(BASE_DIR + '/cookies/zhipin.cookie', 'wb'))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse_job(self, response):
        item = {}
        item_loader = GeneralJobItemLoader(item=GeneralJobItem(), response=response)
        title = response.xpath('//*div[@class="info-primary"]/div[@class="name"]/h1/text()')
        item_loader.add_xpath('title', '//*[@class="info-primary"]/*[@class="name"]/h1/text()')
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        salary = response.css(".job_request .salary::text")
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']//span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']//span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']//span[4]/text()")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()
        return item_loader.load_item()
