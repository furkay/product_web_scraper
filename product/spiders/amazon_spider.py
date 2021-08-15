# coding=utf-8
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import psycopg2
import scrapy
from pypika import Table, PostgreSQLQuery, Order

from product.items import ProductComment
from product.utils import db_creds


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    custom_settings = {
        'ITEM_PIPELINES': {
            'product.pipelines.CommentPipeline': 300,
        }
    }

    def start_requests(self):
        BASE_URL = 'https://www.amazon.com.tr/dp/B08PPYCQM9/ref=asc_df_B08PPYCQM91628001180000' \
            .replace('dp', 'product-reviews')
        BASE_COMMENT_URL = BASE_URL.split('=')[0] + '=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
        yield scrapy.Request(BASE_COMMENT_URL, self.parse_api,
                             meta={'page_index': 0, 'pure_url': BASE_COMMENT_URL})

    def parse_api(self, response):
        page_index = response.meta['page_index']
        pure_url = response.meta['pure_url']
        has_data = True
        if page_index != 0:
            contents = response.css(
                'div.a-size-base div.a-size-base div#cm_cr-review_list div.a-section.review.aok-relative')
            if len(contents) is 0:
                has_data = False
            else:
                for content in contents:
                    comment_title = content.css('div.a-row a.a-size-base.a-link-normal.review-title.a-color-base'
                                                '.review-title-content.a-text-bold '
                                                'span::text').get()
                    comment_username = content.css(
                        'div.a-row.a-spacing-mini a.a-profile div.a-profile-content span.a-profile-name::text').get()
                    comment_content = content.css(
                        'div.a-row.a-spacing-small.review-data span.a-size-base.review-text.review-text-content '
                        'span::text').get()

                    if comment_content is None:
                        comment_content = ''
                    if comment_title is None:
                        comment_title = ''
                    if comment_username is None:
                        comment_username = 'Amazon Kullanıcısı'
                    comment = ProductComment(author=comment_username, comment_title=comment_title,
                                             comment_content=comment_content,
                                             product_id=1, store_url='amazon.com',)
                    yield comment

        page_index = page_index + 1
        page_url = pure_url + '&pageNumber={page_index}'.format(page_index=page_index)
        if has_data:
            yield response.follow(page_url, self.parse_api,
                                  meta={'page_index': page_index, 'pure_url': pure_url, })
