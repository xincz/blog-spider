# coding: utf-8

import os
import time
import pickle
import scrapy
from datetime import datetime
from selenium import webdriver
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5
from settings import BASE_DIR


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*',)), follow=True),
        # Rule(LinkExtractor(allow=('gongsi/j\d+.html',)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_iob', follow=True),
    )

    # 需要重载的方法
    # def parse_start_url(self, response, **kwargs):
    #     return []

    # 需要重载的方法
    # def process_results(self, response, results):
    #     return results

    # 爬虫的入口点，重载此方法
    def start_requests(self):
        # selenium 模拟登录后拿到 cookie 交给 scrapy 的 requests 使用
        # 从文件中读取 COOKIE
        cookies = []
        if os.path.exists(BASE_DIR + '/cookies/lagou.cookie'):
            cookies = pickle.load(open(BASE_DIR + '/cookies/lagou.cookie', 'rb'))

        if not cookies:
            browser = webdriver.Chrome(executable_path='C:/Users/ace01/Downloads/browser_drivers/chromedriver.exe')
            browser.get('https://passport.lagou.com/login/login.html')
            browser.find_element_by_css_selector('.form_body .input.input_white').send_keys('17764534723')
            browser.find_element_by_css_selector('.form_body .input[type="password"]').send_keys('haha1998')
            browser.find_element_by_css_selector('div[data-view="passwordLogin"] input.btn_lg').click()
            time.sleep(10)
            cookies = browser.get_cookies()
            # 将 COOKIE 写入文件，方便下次登录
            pickle.dump(cookies, open(BASE_DIR + '/cookies/lagou.cookie', 'wb'))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse_iob(self, response):
        # 解析拉钩网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        title = response.css('.job-name::attr(title)')
        item_loader.add_css('title', '.job-name::attr(title)')
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        salary = response.css(".job_request .salary::text")
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']//span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']//span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']//span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']//span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()
        return item_loader.load_item()
