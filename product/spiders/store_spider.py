from urllib.parse import urlparse

import psycopg2
import scrapy
from pypika import PostgreSQLQuery, Table, Order

from product.items import ProductSeller
from product.utils import db_creds


class StoreSpider(scrapy.Spider):
    name = 'store'
    custom_settings = {
        'ITEM_PIPELINES': {
            'product.pipelines.StorePipeline': 300,
        }
    }

    def start_requests(self):
        index = 0
        self.connection = psycopg2.connect(host=db_creds.data_hostname, user=db_creds.data_username, password=db_creds.data_pass, dbname=db_creds.data_db_name)
        self.cur = self.connection.cursor()

        while True:
            sellers = self.get_sellers(index * 1000)
            index = index + 1
            if sellers is not None:
                for product_seller in sellers:
                    if 'cimri' in product_seller[2]:
                        yield scrapy.Request(product_seller[2], meta={'id': product_seller[0]})
                    else:
                        continue

    def parse(self, response):
        id = response.meta.get('id')

        for item in response.css('a::attr("href")'):
            non_parsed_link = item.get()
            parsed_link = urlparse(non_parsed_link)
            url = parsed_link.netloc + parsed_link.path
            if 'turkcell' in url:
                url = url.split('url=')[1]
            product_seller = ProductSeller(id=id, product_url=url)
            yield product_seller

    def get_sellers(self, offset):
        tbl_product_sellers = Table('product_sellers')
        get_product = PostgreSQLQuery.from_(tbl_product_sellers).select(tbl_product_sellers.star) \
                          .orderby(tbl_product_sellers.id, order=Order.asc)[offset:1000].get_sql()
        self.cur.execute(get_product)
        p = self.cur.fetchall()
        return p
