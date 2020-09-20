# coding: utf-8

from datetime import datetime
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer

connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class ArticleType(DocType):
    # Cnblogs Type Mappings
    suggest = Completion(analyzer=ik_analyzer)  # careful!
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()  # 全部保存不做分词
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    like_nums = Integer()
    view_nums = Integer()
    comment_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "cnblogs"
        doc_type = "article"


if __name__ == "__main__":
    ArticleType.init()
