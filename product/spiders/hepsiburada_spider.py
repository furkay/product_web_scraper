# coding=utf-8
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import psycopg2
import scrapy
from pypika import Table, PostgreSQLQuery, Order

from product.items import ProductComment
from product.utils import db_creds


class AmazonSpider(scrapy.Spider):
    name = "hepsiburada"

    custom_settings = {
        'ITEM_PIPELINES': {
            'product.pipelines.CommentPipeline': 300,
        }
    }

    def start_requests(self):
        BASE_URL = 'https://www.hepsiburada.com/apple-macbook-air-m1-cip-8gb-256gb-ssd-macos-13-qhd-tasinabilir-bilgisayar-gumus-mgn93tu-a-p-HBV0000130VNJ'

        yield scrapy.Request(BASE_URL, self.parse_api,
                             meta={'page_index': 0, 'pure_url': BASE_URL})

    def parse_api(self, response):
        print('*****requrest')
        page_index = response.meta['page_index']
        pure_url = response.meta['pure_url']
        has_data = True
        if page_index != 0:
            general_content = response.css('span[itemprop="author"]::text').get()
            print(general_content)

        page_index = page_index + 1
        page_url = pure_url + '&-yorumlari?sayfa={page_index}&ozellik='.format(page_index=page_index)
        yield response.follow(page_url, self.parse_api,
                              meta={'page_index': page_index, 'pure_url': pure_url, })
