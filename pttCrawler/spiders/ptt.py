import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.exceptions import CloseSpider,DontCloseSpider
from scrapy.http import Request
from pttCrawler.items import PostItem, AuthorItem, CommentItem
from pttCrawler.settings import MAXIMUM_MISSING_COUNT
from datetime import datetime
import time, logging

'''
Scrapy >> Spider >> RedisSpider
RedisSpider rewrite `from_crawler()` in Spider class
'''

class PTTspider(RedisSpider):

    '''
    If queue is empty, then waits
    While queue is not empty, take a request from the queue
    '''
    name = 'ptt'
    redis_key = 'ptt:start_urls'

    board = None
    year = 2020
    maximum_missing_count = MAXIMUM_MISSING_COUNT
    
    def __init__(self, start=None, end=None, *args, **kwargs):
        
        self.allowed_domains = ['ptt.cc']
        try:
            m_d_start = tuple(map(int, start.split('/')))
            m_d_end = tuple(map(int, end.split('/')))
        
        except AttributeError as err:
            raise CloseSpider(err)
        else:
            self.start = datetime(self.year, m_d_start[0], m_d_start[1])
            self.end = datetime(self.year, m_d_end[0], m_d_end[1])        

        super(PTTspider, self).__init__(*args, **kwargs)
        logging.debug('\n\nCrawling articles from  {} to {}\n\n.'.format(start, end))

    def make_requests_from_url(self, url):
        '''
            There is no `start_requests()` method to get url. \
            This method is used to construct the initial requests in the `start_requests()` method, \
                and is typically used to convert urls to requests.
            It returns Requests with the `parse()` method as their callback function.
        '''
        self.board = url.split('/')[-2]
        return Request(url,
            cookies={'over18':1}, # collect data from sex or Gossiping board.
            dont_filter=True)

    def parse(self, response):
        logging.info('Crawling first page, we crawl the index of ptt: {}'.format(response.request.url))
        # e.g., response.request.url = https://www.ptt.cc/bbs/Soft_Jobs/index.html     
        yield scrapy.Request(response.request.url, 
            callback=self.parse_article,
            dont_filter=True)

    def parse_comment(self, response):
        # create a comment-object to store results
            ''' Post part that processes remaining postItem '''
            post_item = response.meta['post']
            try:
                post_item['content'] = response.xpath("//div[@id='main-content']/text()")[0].extract()
            except IndexError:
                logging.error('Fail to get the content, so give a empty string as a result')
            try:    
                find_head = response.css("div.article-metaline")
                post_item['createdTime'] = find_head[2].css("span.article-meta-value::text")[0].extract()
            except IndexError:
                logging.error('Fail to get time, so give a empty string as a result')
            
            yield post_item    
        
            ''' Author part that processes authoritems '''
            author_item = AuthorItem()
            try:
                find_head = response.css("div.article-metaline")
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
        
            ''' Comment part that processes commentItem '''
            comment_item = response.meta['comment']
            for tag in response.css("div.push"):
                try:
                    comment_item['commentId'] = tag.css("span.push-userid::text")[0].extract()
                    comment_item['commentContent'] = tag.css('span.push-content::text')[0].extract()
                    comment_item['commentTime'] = tag.css('span.push-ipdatetime::text')[0].extract().rstrip()
                except IndexError:
                    logging.error('Fail to crawl the comment')
                else:
                    yield comment_item
                continue
        
    def parse_article(self, response):
       
        comment_item = CommentItem()
        post_item = PostItem()

        # define the next page url
        try:
            next_page = response.xpath("//div[@id='action-bar-container']//a[contains(text(), '上頁')]/@href")[0]
        except:
            next_page = None
            logging.error('Cannot load the next page')
        # see the number of articles
        try:        
            article_list = response.css('.r-list-container > div')
        except:
            logging.error('There is not exist any article being loaded')
        else:
            logging.info('the number of articles is {}'.format(len(article_list)))
            # check all tags of div 
            while len(article_list) > 0:
                div = article_list.pop(0)       
                try:
                    # get class name inside div tag
                    slot_name = div.xpath('@class')[0].extract()
                    # get url inside article respectively
                    canonicalUrl = response.urljoin(div.css('.title a::attr(href)')[0].extract())
                    # get author inside article respectively            
                    author_str = div.css('.author::text')[0].extract()
                except:
                    logging.error('Fail to access url, author and classes')
                
                else:
                    if slot_name == 'r-list-sep':
                        '''
                        Once receiving class='r-list-sep', we are going to crawl the next page.
                        '''
                        if next_page: # exists the next page
                            logging.warning('redirect to following {}'.format(canonicalUrl))
                            yield scrapy.Request(canonicalUrl,
                                callback=self.parse_article,
                                dont_filter=True)
                        else: # there is no following page, we stop the spider and wait for a new request   
                            raise CloseSpider('page exceeded')
                        break # Then we needn't search the following
                    
                    else: # r-ent' or 'search-bar':
                        '''
                            load each article url and find information such as content, comment, author, etc..
                        '''
                        if slot_name != 'r-ent': continue # 'search-bar'
                        
                        ## try to access articles which match the period we defined
                        date_str = div.css('.date::text')[0].extract()
                        m_d = tuple(map(int, date_str.split('/')))
                        m_d = datetime(self.year, m_d[0], m_d[1])
                        in_period =  self.start <= m_d <= self.end
                        logging.debug('the date is {}/{}, and reach or not {}'.format(m_d.month, m_d.day,in_period))        
                        
                        if in_period:      
                            # First get items in an article before loading url inside
                            try:
                                post_item['canonicalUrl'] = canonicalUrl
                                comment_item['canonicalUrl'] = canonicalUrl
                                post_item['authorId']= author_str
                                post_item['title']= div.css('.title a::text')[0].extract()
                                post_item['publishedTime']= date_str
                                post_item['board'] = self.board

                            except IndexError:
                                logging.error('Fail to save object (postItem)')

                            
                            # This part we try to get in url corresponding to article
                            try:
                                url = response.urljoin(div.css('.title a::attr(href)')[0].extract())
                                logging.info('load url inside every article:{}'.format(url))
                                
                                yield scrapy.Request(url,
                                    meta= {'post': post_item,
                                    'comment':comment_item},
                                    callback=self.parse_comment,
                                    dont_filter=True)
                            
                            except IndexError:
                                logging.error('Cannot load article')
                        else:
                            self.maximum_missing_count -= 1
                            
                if len(article_list) == 0:
                    '''
                    Let's go to the next page since we have explored every article
                    '''
                    if next_page and self.maximum_missing_count > 0: # exists the next page
                        url = response.urljoin(next_page.extract())
                        logging.warning('redirect to following {}'.format(url))
                        yield scrapy.Request(url,
                            callback=self.parse_article,
                            dont_filter=True)
                    else: # there is no following page, we stop the spider and wait for a new request   
                        logging.error('Without the next page')
                        # endless running
                        raise DontCloseSpider('page exceeded')
                        # close the spider
                        # raise CloseSpider('page exceeded')