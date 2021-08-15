import scrapy


class Product(scrapy.Item):
    name = scrapy.Field()
    properties = scrapy.Field()
    product_sellers = scrapy.Field()
    product_image_urls = scrapy.Field()


class ProductSeller(scrapy.Item):
    id = scrapy.Field()
    product_url = scrapy.Field()
    price = scrapy.Field()


class ProductComment(scrapy.Item):
    product_id = scrapy.Field()
    comment_title = scrapy.Field()
    comment_content = scrapy.Field()
    author = scrapy.Field()
    store_url = scrapy.Field()
