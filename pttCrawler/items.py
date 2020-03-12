# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class PostItem(scrapy.Item):
    canonicalUrl = scrapy.Field()
    authorId = scrapy.Field()
    title =  scrapy.Field()
    content =scrapy.Field()
    publishedTime = scrapy.Field()
    createdTime = scrapy.Field()
    board = scrapy.Field()

class AuthorItem(scrapy.Item):
    authorId = scrapy.Field()
    authorName = scrapy.Field()

class CommentItem(scrapy.Item):
    commentId = scrapy.Field() # refer to post ID
    canonicalUrl = scrapy.Field() # refer to author ID
    commentContent = scrapy.Field()
    commentTime = scrapy.Field()

    
