# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PostItem(scrapy.Item):
    authorId = scrapy.Field()
    title =  scrapy.Field()
    publishedTime = scrapy.Field()
    content =scrapy.Field()
    canonicalUrl = scrapy.Field()
    createdTime = scrapy.Field()
    updateTime = scrapy.Field()
    board = scrapy.Field()


class AuthorItem(scrapy.Item):
    authorId = scrapy.Field()
    authorName = scrapy.Field()

class CommentItem(scrapy.Item):
    commentId = scrapy.Field()
    commentContent = scrapy.Field()
    commentTime = scrapy.Field()
    board = scrapy.Field()

    
