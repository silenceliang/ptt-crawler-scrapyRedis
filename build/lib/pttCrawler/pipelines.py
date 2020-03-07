# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from .items import PostItem, AuthorItem, CommentItem
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from scrapy.exceptions import DropItem
import re, logging
import pymongo

class MongoPipeline(object):

    collection_name = 'ptt-articles'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        ## how to handle each post
        self.db[self.collection_name].insert(dict(item))
        logging.debug("Post added to MongoDB")
        return item

class JsonPipeline(object):
    
    def __init__(self):
        
        self.article = open('article.json', 'wb')
        self.comment = open('comment.json', 'wb')
        self.author = open('author.json', 'wb')

        self.art_exporter = JsonItemExporter(self.article, encoding="utf-8", ensure_ascii=False)
        self.com_exporter = JsonItemExporter(self.comment, encoding="utf-8", ensure_ascii=False)
        self.aut_exporter = JsonItemExporter(self.author, encoding="utf-8", ensure_ascii=False)
       
        self.art_exporter.start_exporting()
        self.com_exporter.start_exporting()
        self.aut_exporter.start_exporting()

    def close_spider(self, spider):
        
        self.art_exporter.finish_exporting()
        self.com_exporter.finish_exporting()
        self.aut_exporter.finish_exporting()
        
        self.author.close()
        self.article.close()
        self.comment.close()

    def process_item(self, item, spider):
        
        if isinstance(item, PostItem):
            logging.debug("Write post item to json.")
            self.art_exporter.export_item(item)

        elif isinstance(item, CommentItem):
            logging.debug("Write comment item to json.")
            self.com_exporter.export_item(item)

        elif isinstance(item, AuthorItem):
            logging.debug("Write author item to json.")
            pattern = re.compile(r'\((.*)\)')
            match = re.search(pattern, item['authorName'])
            try:
                item['authorName'] = match.group(0)[1:-1]
            except:
                logging.error('This name cannot be update.')
            self.aut_exporter.export_item(item)
        return item

class DuplicatesPipeline(object):
    
    def __init__(self):

        self.author_set = set() # collect the auther id
        # self.post_set = set() # collect the update time

    def process_item(self, item, spider):
        
        # if isinstance(item, PostItem):
        #     logging.debug("filter duplicated post items.")
        #     if item['updateTime'] in self.post_set:
        #         raise DropItem("Duplicate post found:%s" % item)
        #     self.post_set.add(item['updateTime'])
        if isinstance(item, AuthorItem):
            logging.debug("filter duplicated author items.")
            if item['authorId'] in self.author_set:
                raise DropItem("Duplicate author found:%s" % item)
            self.author_set.add(item['authorId'])

        return item

class CsvPipeline(object):
    def __init__(self):    
        self.article = open('article.csv', 'wb')
        self.comment = open('comment.csv', 'wb')
        self.author = open('author.csv', 'wb')
        self.art_exporter = JsonItemExporter(self.article, encoding="utf-8", ensure_ascii=False)
        self.com_exporter = JsonItemExporter(self.comment, encoding="utf-8", ensure_ascii=False)
        self.aut_exporter = JsonItemExporter(self.author, encoding="utf-8", ensure_ascii=False)
       
        self.art_exporter.start_exporting()
        self.com_exporter.start_exporting()
        self.aut_exporter.start_exporting()

    def close_spider(self, spider):
        self.art_exporter.finish_exporting()
        self.com_exporter.finish_exporting()
        self.aut_exporter.finish_exporting()
        
        self.author.close()
        self.article.close()
        self.comment.close()

    def process_item(self, item, spider):
        if isinstance(item, PostItem):
            self.art_exporter.export_item(item)

        elif isinstance(item, CommentItem):
            self.com_exporter.export_item(item)

        elif isinstance(item, AuthorItem):
            logging.debug("Add to Author json")
            pattern = re.compile(r'\((.*)\)')    
            match = re.search(pattern, item['authorName'])
            item['authorName'] = match.group(0)[1:-1]
            self.aut_exporter.export_item(item)

        return item