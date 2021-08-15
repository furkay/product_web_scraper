import os

import certifi
import scrapy

from product.items import Product, ProductSeller

os.environ["SSL_CERT_FILE"] = certifi.where()


class CimriProductSpider(scrapy.Spider):
    name = "cimri_product"

    BASE_URL = 'https://www.cimri.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'product.pipelines.ProductPipeline': 300,
        }
    }

    def start_requests(self):
        filename = os.getcwd() + '/.cache/product_urls.txt'
        with open(filename, 'r') as f:
            product_relative_links = f.readlines()
        return list(
            map(lambda x: scrapy.Request(CimriProductSpider.BASE_URL + x, dont_filter=True,
                                         ), product_relative_links))

    async def parse(self, response):
        properties = {}
        product_sellers = []
        property_list = []
        product_image_urls = []
        title = None

        for img in response.css('ul li img'):
            url_set = img.css('::attr("srcset")').get()
            if url_set is not None:
                url = img.css('::attr("src")').getall()
                product_image_urls = url

        for itemProperty in response.css('div div div div[name] ul li'):
            span = itemProperty.css('span')
            if span is not None:
                spans = span.xpath('text()').getall()
                if len(spans) == 0:
                    if title is not None:
                        properties[title] = property_list
                        property_list = []
                    title = itemProperty.xpath('text()').get()
                else:
                    pro = {spans[0]: spans[1]}
                    property_list.append(pro)

        for itemStore in response.css('table tbody tr'):
            link = itemStore.css('td a::attr("href")').get()
            price = itemStore.css('td div::text').getall()
            product_sellers.append(ProductSeller(product_url=link, price=price[-1]))

        item_name = response.css('div div h1')
        product = Product(name=str(item_name.xpath('text()').get()), properties=str(properties),
                          product_sellers=product_sellers, product_image_urls=product_image_urls)

        return product
