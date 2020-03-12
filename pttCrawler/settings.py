# -*- coding: utf-8 -*-

# Scrapy settings for pttCrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'pttCrawler'
SPIDER_MODULES = ['pttCrawler.spiders']
NEWSPIDER_MODULE = 'pttCrawler.spiders'
FEED_EXPORT_ENCODING = 'utf-8'

# The limit amount of visited pages
MAXIMUM_MISSING_COUNT = 500

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'pttCrawler (+http://www.yourdomain.com)'
UserAgentList = [
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'
]
# Obey robots.txt rules
# ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable scheduling storing requests queue in redis
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'

# Ensure all spiders share same duplicates filter through redis
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
DUPEFILTER_DEBUG = True
# Whether to flush requests when closing.
SCHEDULER_PERSIST = True

# local
# REDIS_HOST = 'localhost'
# docker
REDIS_HOST = 'redis'
REDIS_PORT = 6379

# slaver crawler settings
# REDIS_URL = 'redis://root:123456@ip:6379'
# REDIS_PORT = 6379

# If we encounter following http code, we retry to visit until over 10 times
RETRY_TIMES = 10
RETRY_HTTP_CODES = [500,502,503,504,522,524,408,429,520]

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'pttCrawler.middlewares.PttcrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    pttCrawler.middlewares.PttcrawlerDownloaderMiddleware': 543,
    'pttCrawler.middlewares.RandomUserAgentMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'pttCrawler.pipelines.DuplicatesPipeline':300,
    'pttCrawler.pipelines.JsonPipeline': 400,
    'pttCrawler.pipelines.MongoPipeline': 500,
}

## MONGODB settings
MONGO_DATABASE = 'ptt-sandbox'
# local
# MONGO_URI = 'mongodb://localhost:27017'
# docker
MONGO_URI = 'mongodb://mongodb:27017'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [520]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

## Notify user by email
mail_settings = {
    'MAIL_FROM' : 'scrapy@localhost',
    'MAIL_HOST' : 'localhost',
    'MAIL_PORT' : 25,
    'MAIL_USER' : None,
    'MAIL_PASS' : None
}

