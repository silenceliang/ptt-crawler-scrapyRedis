# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
from scrapy.exceptions import DropItem
from .items import PostItem, AuthorItem, CommentItem
import re, logging
import pymongo

## Here we save data in mongo DB where priority is assigned to 3th. 
class MongoPipeline(object):

    collection_post = 'post'
    collection_author = 'author'
    collection_comment = 'comment'

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
        if isinstance(item, PostItem):
            post = dict(item)
            post.update(_id=post.pop('canonicalUrl'))
            self.db[self.collection_post].insert(post)

        elif isinstance(item, CommentItem):
            self.db[self.collection_comment].insert(dict(item))

        elif isinstance(item, AuthorItem):
            author = dict(item)
            author.update(_id=author.pop('authorId'))
            self.db[self.collection_author].insert(author)
           
        logging.debug("Post added to MongoDB")
        return item
## Here we project data onto json script where priority is assigned to 2th. 
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
        
        self.article.close()
        self.comment.close()
        self.author.close()

    def process_item(self, item, spider):
        
        if isinstance(item, PostItem):
            logging.debug("Write post item to json.")
            item['publishedTime'] = item['publishedTime'].strip()
            self.art_exporter.export_item(item)

        elif isinstance(item, CommentItem):
            logging.debug("Write comment item to json.")
            item['commentTime'] = item['commentTime'].strip()
            item['commentContent'] = item['commentContent'][2:]
            self.com_exporter.export_item(item)

        elif isinstance(item, AuthorItem):
            logging.debug("Write author item to json.")
            pattern = re.compile(r'\((.*)\)')
            match = re.search(pattern, item['authorName'])
            try:
                item['authorName'] = match.group(0)[1:-1]
            except:
                logging.error('This name cannot be update')
            self.aut_exporter.export_item(item)
        
        return item
## Here we filter data tp avoid duplicates where priority is assigned to 1th. 
class DuplicatesPipeline(object):
    
    def __init__(self):
        # collection of comment is a many-to-many relationship, we don't need to filter that
        self.author_set = set() # collect the auther id
        self.post_set = set() # collect the canonicalUrl

    def process_item(self, item, spider):
        
        if isinstance(item, PostItem):
            logging.debug("filter duplicated post items.")
            if item['canonicalUrl'] in self.post_set:
                raise DropItem("Duplicate post found:%s" % item)
            self.post_set.add(item['canonicalUrl'])
        
        elif isinstance(item, AuthorItem):
            logging.debug("filter duplicated author items.")
            if item['authorId'] in self.author_set:
                raise DropItem("Duplicate author found:%s" % item)
            self.author_set.add(item['authorId'])

        return item
