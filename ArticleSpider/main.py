# coding: utf-8

import os
import sys
from scrapy.cmdline import execute

# 项目根目录：os.path.dirname(__file__)
sys.path.append(os.path.abspath(__file__))

execute(['scrapy', 'crawl', 'cnblogs'])
# execute(['scrapy', 'crawl', 'zhihu'])
# execute(['scrapy', 'crawl', 'lagou'])
