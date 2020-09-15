# coding: utf-8

import re
import json
from urllib import parse

import requests
import scrapy
from scrapy import Request, Selector
# from scrapy.loader import ItemLoader

# 使用自定义的 ItemLoader
from ArticleSpider.items import ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import CnblogsArticleItem

class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    def parse(self, response):
        """
        1. 获取新闻列表页中的 url 并交给 scrapy 进行下载后调用相应的解析方法
        2. 获取下一页的 url 并交给 scrapy 进行下载，下载完成后交给 parse 继续跟进
        """
        # url = response.xpath('//*[@id="entry_672279"]/div[2]/h2/a/@href').extract_first("")
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        # sel = Selector(text=response.text)
        # urls = response.css('div#news_list h2.news_entry a::attr(href)').extract()

        # Start here
        post_nodes = response.css('#news_list div.news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            post_url = post_node.css('h2.news_entry a::attr(href)').extract_first("")
            # 打开正文页面，继续爬取 -- 需要一次 yield
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={'front_image_url': image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给 scrapy 进行下载
        next_name = response.css("div.pager a:last-child::text").extract_first("")
        # next_url = response.xpath('//a[contains(text(),"Next >")]/@href').extract_first("")
        if next_name == "Next >":
            next_url = response.css("div.pager a:last-child::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)
            # title = response.css("#news_title a::text").extract_first("")
            # title = response.xpath("//*[@id='news_title']//a/text()").extract_first("")
            # create_date = response.css("#news_info .time::text").extract_first("")
            # create_date = response.xpath("//*[@id='news_info']//*[@class='time']/text()").extract_first("")
            # date_re = re.match(".*?(\d+.*)", create_date)
            # if date_re:
            #     create_date = date_re.group(1)
            # content = response.css("#news_content").extract_first("")
            # content = response.xpath("//*[@id='news_content']").extract_first("")
            # tag_list = response.css(".news_tags a::text").extract()
            # tag_list = response.xpath("//*[@class='news_tags']//a/text()").extract()
            # tags = ",".join(tag_list)

            # 赋值
            # article_item = CnblogsArticleItem()
            # article_item['title'] = title
            # article_item['create_date'] = create_date
            # article_item['content'] = content
            # article_item['tags'] = tags
            # article_item['url'] = response.url
            # if response.meta.get("front_image_url", ""):
            #     front_image_url = response.meta.get("front_image_url", "")
            #     if not re.match('^https:.*', front_image_url):
            #         front_image_url = 'https:' + front_image_url
            #     article_item['front_image_url'] = [front_image_url]
            # else:
            #     article_item['front_image_url'] = []

            # 注意：使用绝对路径！直接加到域名后面！
            # 这是一个同步请求，后续的代码会被 block
            # html = requests.get(parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            # json_data = json.loads(html.text)

            # Use ItemLoader
            item_loader = ArticleItemLoader(item=CnblogsArticleItem(), response=response)
            item_loader.add_xpath('title', "//*[@id='news_title']//a/text()")
            item_loader.add_xpath('content', "//*[@id='news_content']")
            item_loader.add_xpath('tags', "//*[@class='news_tags']//a/text()")
            item_loader.add_xpath('create_date', "//*[@id='news_info']//*[@class='time']/text()")
            item_loader.add_value('url', response.url)
            item_loader.add_value('front_image_url', response.meta.get('front_image_url', ''))

            # article_item = item_loader.load_item()

            # 使用异步请求
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"item_loader": item_loader, "url_object_id": get_md5(response.url)},
                          callback=self.parse_nums)

            # like_nums = json_data['DiggCount']
            # view_nums = json_data['TotalView']
            # comment_nums = json_data['CommentCount']


    def parse_nums(self, response):
        json_data = json.loads(response.text)

        item_loader = response.meta.get("item_loader")

        item_loader.add_value("like_nums", json_data['DiggCount'])
        item_loader.add_value("view_nums", json_data['TotalView'])
        item_loader.add_value("comment_nums", json_data['CommentCount'])
        item_loader.add_value("url_object_id", response.meta.get('url_object_id'))

        # article_item["like_nums"] = json_data['DiggCount']
        # article_item["view_nums"] = json_data['TotalView']
        # article_item["comment_nums"] = json_data['CommentCount']
        # article_item["url_object_id"] = get_md5(article_item["url"])

        yield item_loader.load_item()
        # 所有的方法里都可以随时去 yield request / item (必须是这两种类型)
        # 如果是 request, 会走 scrapy 下载的逻辑
        # 如果是 item, 会进入 pipeline 来进行处理 -- 无论是进入数据库还是其他操作
        # 由自己定义
        # 任何方法里都可以 yield request / item