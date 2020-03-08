import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.log import configure_logging  
from scrapy.exceptions import CloseSpider
from pttCrawler.items import PostItem, AuthorItem, CommentItem
from datetime import datetime
import time, logging

'''
Scrapy >> Spider >> RedisSpider
RedisSpider rewrite `from_crawler()` in Spider class
'''

class PTTspider(RedisSpider):
    # log initialize
    configure_logging(install_root_handler=False) 
    logging.basicConfig ( 
        filename = 'logging.txt', 
        format = '%(levelname)s: %(message)s', 
        level = logging.INFO)

    '''
    If queue is empty, then waits
    While queue is not empty, take a request from the queue
    '''
    name = 'ptt'
    redis_key = 'ptt:start_urls'
    board = None

    def __init__(self, start=None, end=None, *args, **kwargs):
        m_d_start = [int(x) for x in start.split('/')]
        m_d_end = [int(x) for x in end.split('/')]
        self.year = 2020
        self.start = datetime(self.year, m_d_start[0], m_d_start[1])
        self.end = datetime(self.year, m_d_end[0], m_d_end[1])
        self.maximum_missing_count = 500
        super(PTTspider, self).__init__(*args, **kwargs)
        logging.debug('\n\nCrawling articles from  {} to {}\n\n.'.format(start, end))

    def parse(self, response):
        logging.info('Crawling first page, we crawl the index of ptt: {}'.format(response.request.url))
        # e.g., response.request.url = https://www.ptt.cc/bbs/Soft_Job/index.html
        
        self.board = response.request.url.split('/')[-2]

        yield scrapy.Request(response.request.url, 
            cookies={'over18':1}, # To collect data from sex or Gossiping board.
            callback=self.parse_article,
            dont_filter = True) 

    def parse_comment(self, response):
        # create a comment-object to store results
        post_item = response.meta['post']
        try:
            post_item['content'] = response.xpath("//div[@id='main-content']/text()")[0].extract()
        except IndexError:
            post_item['content'] = ''
            logging.error('Fail to get the content, so give a empty string as a result')
        try:    
            find_head = response.css("div.article-metaline")
            post_item['createdTime'] = find_head[2].css("span.article-meta-value::text")[0].extract()
            post_item['updateTime'] = find_head[2].css("span.article-meta-value::text")[0].extract()
        except IndexError:
            post_item['createdTime'] = ''
            post_item['updateTime'] = ''
            logging.error('Fail to get time, so give a empty string as a result')
        
        yield post_item
       
        author_item = response.meta['author']
        try:
            author_item['authorName'] = find_head[0].css("span.article-meta-value::text")[0].extract()
        except IndexError:
            author_item['authorName'] = '' 
            logging.error('Fail to get the authorName, so give a empty string as a result')
        try:
            author_item['authorId'] = post_item['authorId']
        except IndexError:
            author_item['authorId'] = ''
            logging.error('Fail to get the authorId, so give a empty string as a result')

        yield author_item

        comment_item = CommentItem() 
        comment_item['board'] = self.board
        target = response.css("div.push")
        for tag in target:
            try:
                comment_item['commentId'] = tag.css("span.push-userid::text")[0].extract()
                comment_item['commentContent'] = tag.css('span.push-content::text')[0].extract()
                comment_item['commentTime'] = tag.css('span.push-ipdatetime::text')[0].extract().rstrip()
                yield comment_item
            except IndexError:
                logging.error('Fail to crawl comment')
            continue

    def parse_article(self, response):
        # create a post-object to store results
        post_item = PostItem()
        post_item['board'] = self.board
        # create a author-object to store results
        author_item = AuthorItem()    
        # define the next page url
        try:
            next_page = response.xpath("//div[@id='action-bar-container']//a[contains(text(), '上頁')]/@href")[0]
        except:
            next_page = None
            logging.error('Cannot read the next page')
        
        article_list = response.css('.r-list-container > div')
        logging.info('the length of page is {}'.format(len(article_list)))
        # check all tags of div 
        while len(article_list) > 0:
            div = article_list.pop(0)
            # get class name inside div tag
            slot_name = div.xpath('@class')[0].extract()
            '''
                once receiving 'r-list-sep', we are going to crawl the next page
            '''
            if slot_name == 'r-list-sep':
                if next_page: # exists the next page
                    url = response.urljoin(next_page.extract())
                    logging.warning('redirect to following {}'.format(url))
                    yield scrapy.Request(url,
                        cookies={'over18':1},
                        callback=self.parse_article,
                        dont_filter = True
                        )
                else: # there is no following page, we stop the spider and wait for a new request   
                    logging.error('Without the next page')
                    raise CloseSpider('page_exceeded')
                break # Then we needn't search the following
            
            else: # r-ent' or 'search-bar':
                '''
                    load each article url and find information such as content, comment, author ...
                '''
                if slot_name != 'r-ent': continue # 'search-bar'
                date_str = div.css('.date::text')[0].extract()
                m_d = [int(x) for x in date_str.split('/')]
                m_d = datetime(self.year, m_d[0], m_d[1])
                in_period =  self.start <= m_d <= self.end
                logging.debug('the date is {}/{}, and reach or not {}'.format(m_d.month, m_d.day,in_period))
                if in_period:          
                    # First get items in an article before loading url inside
                    try:
                        post_item['publishedTime'] = date_str
                        post_item['canonicalUrl'] = response.urljoin(div.css('.title a::attr(href)')[0].extract())
                        post_item['title'] = div.css('.title a::text')[0].extract()
                        post_item['authorId'] = div.css('.author::text')[0].extract()
                    except IndexError:  # list is empty
                        logging.error('Fail to save object (postItem)')
                    # This part we try to get the url inside article
                    try:
                        url = response.urljoin(div.css('.title a::attr(href)')[0].extract())
                        logging.info('load url inside every article:{}'.format(url))
                        yield scrapy.Request(url,
                            meta= {'post': post_item, 'author': author_item},
                            callback=self.parse_comment,
                            dont_filter = True
                            )
                    except IndexError:
                        logging.error('Cannot load article')
                else:
                    self.maximum_missing_count -= 1
                          
            if len(article_list) == 0:

                if next_page and self.maximum_missing_count > 0: # exists the next page
                    url = response.urljoin(next_page.extract())
                    logging.warning('redirect to following {}'.format(url))
                    yield scrapy.Request(url,
                        cookies={'over18':1},
                        callback=self.parse_article,
                        dont_filter = True)
                else: # there is no following page, we stop the spider and wait for a new request   
                    logging.error('Without the next page')
                    raise CloseSpider('page_exceeded')