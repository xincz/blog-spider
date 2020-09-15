# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import datetime
from w3lib.html import remove_tags

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Identity, Join
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

def date_convert(value):
    date_re = re.match(".*?(\d+.*)", value)
    if date_re:
        return date_re.group(1)
    else:
        return '1970-07-01 00:00'


def http_convert(value):
    if value:
        if not re.match('^https:.*', value):
            value = 'https:' + value
    return value


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class CnblogsArticleItem(scrapy.Item):
    # Each field is represented as a list!
    title = scrapy.Field()
    create_date = scrapy.Field(input_processor=MapCompose(date_convert))
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(input_processor=MapCompose(http_convert), output_processor=Identity())
    front_image_path = scrapy.Field()
    like_nums = scrapy.Field()
    view_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    tags = scrapy.Field(output_processor=Join(separator=','))
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into cnblogs_article(
                title, url, url_object_id, front_image_url, 
                front_image_path, like_nums, view_nums, comment_nums, 
                tags, content, create_date)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE like_nums=VALUES(like_nums)
        """
        params = list()
        params.append(self.get('title', ""))
        params.append(self.get('url', ""))
        params.append(self.get('url_object_id', ""))
        params.append(",".join(self.get('front_image_url', [])))
        params.append(self.get('front_image_path', ""))
        params.append(self.get('like_nums', 0))
        params.append(self.get('view_nums', 0))
        params.append(self.get('comment_nums', 0))
        params.append(self.get('tags', ""))
        params.append(self.get('content', ""))
        params.append(self.get('create_date', "1970-07-01 00:00"))

        return insert_sql, tuple(params)


# Lagou related
def remove_splash(value):
    return value.replace("/", "")


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    # 拉钩网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(input_processor=MapCompose(remove_splash))
    work_years = scrapy.Field(input_processor=MapCompose(remove_splash))
    degree_need = scrapy.Field(input_processor=MapCompose(remove_splash))
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(input_processor=MapCompose(remove_tags, handle_jobaddr))
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(input_processor=Join(","))
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("salary", ""),
            self.get("job_city", ""),
            self.get("work_years", ""),
            self.get("degree_need", ""),
            self.get("job_type", ""),
            self.get("publish_time", "0000-00-00"),
            self.get("job_advantage", ""),
            self.get("job_desc", ""),
            self.get("job_addr", ""),
            self.get("company_name", ""),
            self.get("company_url", ""),
            self.get("job_addr", ""),
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params




