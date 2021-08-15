import os

import scrapy


class CimriSpider(scrapy.Spider):
    name = "cimri"

    BASE_URL = 'https://www.cimri.com/elektronik'

    start_urls = [
        BASE_URL,
    ]

    index = 1

    def parse(self, response):

        filename = os.getcwd() + '/.cache/product_urls.txt'

        with open(filename, 'a') as f:
            for product in response.css('div#cimri-product article'):
                item_link = product.css('a.link-detail::attr("href")').get()
                if item_link is not None:
                    f.write(item_link + '\n')
        next_page = f'https://www.cimri.com/elektronik?page={CimriSpider.index}'
        if CimriSpider.index <= 50:
            CimriSpider.index += 1
            yield response.follow(next_page, self.parse)
