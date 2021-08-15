# coding=utf-8
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import psycopg2
import scrapy
from pypika import Table, PostgreSQLQuery, Order

from product.items import ProductComment
from product.utils import db_creds


class AmazonSpider(scrapy.Spider):
    name = "trendyol"
    custom_settings = {
        'ITEM_PIPELINES': {
            'product.pipelines.CommentPipeline': 300,
        }
    }

    def start_requests(self):
        BASE_URL = 'https://www.trendyol.com/samsung/galaxy-tab-a7-sm-t500-32-gb-10-4-tablet-gri-p-55833750/yorumlar'
    #    parse_url = urlparse(BASE_URL)
    #    url = parse_url.netloc + parse_url.path + '/yorumlar?' + parse_url.query
        yield scrapy.Request(BASE_URL, self.parse)

    def parse(self, response):
        for item in response.css('div.rnr-com-w'):
            comment = item.css('div.rnr-com-tx')
            comment_content = comment.css('::text').get()
            comment_author = item.css('div.rnr-com-bt div span.rnr-com-usr::text').get()
            comment_title = ''
            store_url = 'trendyol.com'
            product_comment = ProductComment(
                comment_title=comment_title,
                author=comment_author,
                comment_content=comment_content,
                store_url = store_url,
                product_id = 1,
            )
            yield product_comment



