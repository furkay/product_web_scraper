from datetime import datetime
from urllib.parse import urlparse, parse_qs

import psycopg2
import scrapy
from pypika import Table, PostgreSQLQuery, Order

from product.items import ProductComment
from product.utils import db_creds


class N11Spider(scrapy.Spider):
    name = "n11"
    N11_API = 'https://www.n11.com/component/render/productReviews'
    BASE_URL = 'https://www.n11.com/urun/samsung-galaxy-a51-256-gb-samsung-turkiye-garantili-1988862?magaza=samsungturkiye'

    start_urls = [
        BASE_URL
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'product.pipelines.CommentPipeline': 300,
        }
    }

    def parse(self, response):
        product_id = response.css('a.btn.btnGrey.addBasketUnify::attr("data-uniproductid")').get()
        yield response.follow(N11Spider.N11_API + '?page={page_index}&productId={product_id}'.
                              format(page_index='1', product_id=product_id),
                              self.parse_api, meta={'meta_product_id': 1})

    def parse_api(self, response):
        db_product_id = response.meta['meta_product_id']
        parsed_link = urlparse(response.url)
        print('test')
        print(db_product_id)
        product_id = parse_qs(parsed_link.query)['productId'][0]
        print(product_id)
        page_index = int(parse_qs(parsed_link.query)['page'][0])
        page_index = page_index + 1
        next_page = N11Spider.N11_API + '?page={page_index}&productId={product_id}'.format(page_index=str(page_index),
                                                                                           product_id=product_id)
        has_data = response.css('html')
        print(has_data)
        print(next_page)

        if has_data is not None:
            for comment in response.css('li.comment'):
                user_name = comment.css('div.commentTop span.userName::text').get()
                comment_title = comment.css('h5.commentTitle::text').get()
                comment_content = comment.css('p::text').get()
                if user_name is None:
                    user_name = ''
                if comment_title is None:
                    comment_title = ''
                if comment_content is None:
                    comment_content = ''

                comment = ProductComment(author=user_name, comment_title=comment_title, comment_content=comment_content,
                                         product_id=db_product_id, store_url='n11.com',)
                yield comment
            if next_page is not None:
                yield response.follow(next_page, self.parse_api, meta={'meta_product_id': db_product_id})

