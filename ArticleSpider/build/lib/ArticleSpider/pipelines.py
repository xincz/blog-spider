# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import MySQLdb
from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ""
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item


class JsonWithEncodingPipeline(object):
    # 自定义 JSON 文件的导出
    def __init__(self):  # when running scrapy will first call this method
        self.file = codecs.open("article.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # Open file
    def __init__(self):  # when running scrapy will first call this method
        self.file = open('article_export.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlPipeline(object):
    # 采用同步的机制写入 MySQL
    def __init__(self):
        self.conn = MySQLdb.connect(
            "127.0.0.1", 'root', '',
            'spider_article', charset='utf8',
            use_unicode=True
        )
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 解析速度远远大于入库速度，将以下同步代码改为异步
        insert_sql = """
            insert into cnblogs_article(
                title, url, url_object_id, front_image_url, 
                front_image_path, like_nums, view_nums, comment_nums, 
                tags, content, create_date)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = list()
        params.append(item.get('title', ""))
        params.append(item.get('url', ""))
        params.append(item.get('url_object_id', ""))
        params.append(",".join(item.get('front_image_url', [])))
        params.append(item.get('front_image_path', ""))
        params.append(item.get('like_nums', 0))
        params.append(item.get('view_nums', 0))
        params.append(item.get('comment_nums', 0))
        params.append(item.get('tags', ""))
        params.append(item.get('content', ""))
        params.append(item.get('create_date', "1970-07-01 00:00"))

        self.cursor.execute(insert_sql, tuple(params))
        self.conn.commit()
        return item


class MysqlTwistedPipeline(object):
    # 采用异步的机制写入 MySQL, 适用于不同数据表
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        from MySQLdb.cursors import DictCursor
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用 twisted 将 mysql 插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的 item 构建不同的 sql 语句并插入到 mysql 中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class ElasticSearchPipeline(object):
    # Write data into ElasticSearch

    def process_item(self, item, spider):
        # transfer items into ES data
        item.save_to_es()
        return item
