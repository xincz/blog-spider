# coding: utf-8

import time
import scrapy
from selenium import webdriver
from mouse import move, click

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    # 覆盖此方法，完成模拟登录
    def start_requests(self):
        """
        1. 启动 Chrome, 确保所有的 Chrome 实例都已经关闭
        2. 手动启动 chromedriver, 虚拟出 Chrome 启动环境
        """
        ###### Method 1 ######
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

        browser = webdriver.Chrome(executable_path='C:/Users/ace01/Downloads/chromedriver.exe',
                                   chrome_options=chrome_option)
        # browser = webdriver.Chrome(executable_path='C:/Users/ace01/Downloads/chromedriver.exe')
        browser.get('https://www.zhihu.com/signin')
        # browser.find_element_by_css_selector('.SignFlow-tabs div:nth-child(2)').click()
        browser.find_elements_by_css_selector(".SignFlow-tab")[1].click()
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper .Input').send_keys(Keys.CONTROL+'a')
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper .Input').send_keys('17764534723')
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys(Keys.CONTROL+'a')
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys('hanser1998')
        move(534, 630)
        time.sleep(3)
        click()
        browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
        time.sleep(60)

        ###### Method 2 ######
        # browser = webdriver.Edge(executable_path='C:/Users/ace01/Downloads/edgedriver_win64/msedgedriver.exe')
        # browser.get('https://www.zhihu.com/signin')
        # browser.find_elements_by_css_selector(".SignFlow-tab")[1].click()
        # browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper .Input').send_keys('17764534723')
        # browser.find_element_by_css_selector('.SignFlow-password input').send_keys('hanser1998')
        # browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()

    def parse(self, response):
        pass
