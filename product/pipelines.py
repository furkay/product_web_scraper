import psycopg2
from pypika import Table, PostgreSQLQuery

from product.utils.db_creds import data_hostname, data_username, data_pass, data_db_name


class ProductPipeline(object):

    def open_spider(self, spider):
        self.connection = psycopg2.connect(host=data_hostname, user=data_username, password=data_pass,
                                           dbname=data_db_name)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.add_product(item)
        return item

    def add_product(self, item):
        tbl_product = Table('product')
        tbl_product_sellers = Table('product_sellers')
        insert_product = PostgreSQLQuery.into(tbl_product).columns('name', 'properties', 'product_image_urls') \
            .insert(item['name'], item['properties'], str(item['product_image_urls'])).returning('product_id').get_sql()

        product_sellers = item['product_sellers']

        self.cur.execute(insert_product)
        product_id = self.cur.fetchall()[0][0]
        for seller in product_sellers:
            if seller['product_url'] is not None:
                insert_sellers = PostgreSQLQuery.into(tbl_product_sellers).columns('product_id', 'product_url', 'price') \
                    .insert(product_id, seller['product_url'], seller['price']).get_sql()
                self.cur.execute(insert_sellers)

        self.connection.commit()


class StorePipeline(object):

    def open_spider(self, spider):
        self.connection = psycopg2.connect(host=data_hostname, user=data_username, password=data_pass,
                                           dbname=data_db_name)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        tbl_product_sellers = Table('product_sellers')
        update_seller = PostgreSQLQuery.update(tbl_product_sellers) \
            .set(tbl_product_sellers.product_url, item['product_url']).where(
            tbl_product_sellers.id == item['id']).get_sql()
        self.cur.execute(update_seller)
        self.connection.commit()
        return item


class CommentPipeline(object):

    def open_spider(self, spider):
        print('start')
        self.connection = psycopg2.connect(host=data_hostname, user=data_username, password=data_pass,
                                           dbname=data_db_name)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        print('closed')
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        print('end')
        tbl_comments = Table('comments')
        insert_comment = PostgreSQLQuery.into(tbl_comments).\
            columns('product_id', 'comment_title', 'author', 'comment_content', 'store_url').\
            insert(item['product_id'], item['comment_title'], item['author'], item['comment_content'], item['store_url']).get_sql()
        self.cur.execute(insert_comment)
        self.connection.commit()
        return item
