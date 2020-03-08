# pttCrawler
In this project we try to collect data from the ptt website. We adopt scrapy framework based on python language and use mongoDB as our storage. However, crawler handles it job only on single machine. To explore efficently, scrapy-redis provides distributed mechanism that helps us running spider on clients. For the purpose of deployment, we use scrapyd to achieve it. 
- [pttCrawler](#pttcrawler)
  * [Dependencies](#dependencies)
  * [Requirements](#requirements)
  * [Usage](#usage)
    + [Running spider by following command:](#running-spider-by-following-command-)
    + [Start the redis server and get in terminal](#start-the-redis-server-and-get-in-terminal)
    + [Before crawling, we need to obtain the authentication by specific keyword](#before-crawling--we-need-to-obtain-the-authentication-by-specific-keyword)
    + [Push url to redis and running Crawler](#push-url-to-redis-and-running-crawler)
  * [SnapShot](#snapshot)
    + [Result in db](#result-in-db)
    + [Terminal example](#terminal-example)
  * [Collections](#collections)
    + [Post](#post)
    + [Author](#author)
    + [Comment](#comment)
  * [Scrapy-Redis Framework](#scrapy-redis-framework)
    + [Distributed crawler](#distributed-crawler)
    + [Benefits](#benefits)
      - [filter dumplicates](#filter-dumplicates)
      - [scheduler persist](#scheduler-persist)
    + [Deploy with scrapyd](#deploy-with-scrapyd)
  * [Pipeline](#pipeline)
    + [DuplicatesPipeline](#duplicatespipeline)
    + [MongoPipeline](#mongopipeline)
    + [JsonPipeline](#jsonpipeline)
  * [Supplement](#supplement)
  * [Reference](#reference)

## Dependencies
Full dependency installation on Ubuntu 16.04
- **Python 3** (tested on python 3.7.2)
- **redis 3.4.1** 

## Requirements
- **pymongo 3.10.1** (used nosql db)
- **Scrapy 2.0.0** (framework of crawler)
- **scrapy-redis 0.6.8** (achieve distributed scrawling)
- **scrapyd 1.2.1** (provide a crawling daemon )
- **scrapyd-client 1.1.0** (used to deploy our spider)

## Usage

### Running spider by following command: 
```bash
scrapy crawl ptt -a start={m/d} -a end={m/d}
```
* where `-a` received an argument that is a parameter to the spider.<br>
* `{m/d}` means **month/day**. 3/5 just represents March 5th.<br> For example, the command would be `scrapy crawl ptt -a start=3/5 -a end=3/8`

### Start the redis server and get in terminal
```bash
redis-cli
```

### Before crawling, we need to obtain the authentication by specific keyword 
```bash
auth yourpassword
```
* where yourpassword is in `setting.py` and it can be modified directly.

### Push url to redis and running Crawler
```bash
lpush ptt:start_urls https://www.ptt.cc/{board}/index.html
```
* where `{board}` can be described Soft_Job, Gossiping or etc.

## SnapShot

### Result in db
![post info](/assets/img/Screenshot%20from%202020-03-08%2013-23-04.png?raw=true "post item")

### Terminal example
![terminal setup](/assets/img/Screenshot%20from%202020-03-08%2015-23-32.png?raw=true "terminal")


## Collections 
There are three collections in mongoDB:
* Post
* Author
* Comment

### Post
| schema | Description |
| --- | --- |
| *canonicalUrl | url where the page visited |
| authorId | who post the article |
| title | title in the article |
| content | content in the article |
| publishedTime | the date this post was created |
| updateTime | the date this post was updated |
| board | what post belong with in ptt |

### Author
| schema | Description |
| --- | --- |
| *authorId | who post the article |
| authorName | the author's nickname |

### Comment
| schema | Description |
| --- | --- |
| commentId |  who post the conmment |
| commentTime | when user posted |
| commentContent | the content in comment |
| board | what comment belong with in ptt |

**Note**: where schema prefix * represents primary key.

----

## Scrapy-Redis Framework

### Distributed crawler

- master-slaver architecture

1. the master runs spider by following command:
```bash
scrapy crawl pttCrawl
```
2. start redis service and run it :
```bash
redis-cil
```
3. the most important step is to push your url that you attempt to crawl. Here, we use `lpush` to attain this goal. The following redis key is `pttCrawl:start_urls`. We push urls to redis.
```bash
lpush pttCrawl:start_urls {ptt url}
```
4. (optimal) wake our slaver machines up which have a little bit different declaration in `setting.py`:
```bash
scrapy crawl pttCrawl
```

### Benefits

#### filter dumplicates
In `setting.py`, we just add a line that would prevent from repetitive redirection:
```
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
```
#### scheduler persist
In `setting.py`, we just add a line that can keep tracking processes of the crawler. As requests in the redis queue just exist after crawling process stopped. It make convenient start to crawl again. 
```
SCHEDULER_PERSIST = True
```

### Deploy with scrapyd
1. scrapyd provide a daemon for crawling. Like http server, we run it by typing the following command:
```bash
scrapyd
```

2. for the purpose of deployment, we install the package `scrapy-client` and run it:
```bash
scrapyd-deploy pttCrawler
```

## Pipeline
### DuplicatesPipeline
> In case of dumplicates in database, we filter the data here.
```python
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
```

### MongoPipeline
> save data in mongodb. 

### JsonPipeline
> generate a json file.

## Supplement

In the main spider script `ptt.py`, for the sake of convenience we restrict the date stuck in year 2020.<br>
Also, we set `maximum_missing_count` as 500 where aims to control the bound of exploring articles. If there has been no page can be visited or got the limit of our missing count, we then stop crawling so that waste less resource.

```python
class PTTspider(RedisSpider):
    configure_logging(install_root_handler=False) 
    logging.basicConfig ( 
        filename = 'logging.txt', 
        format = '%(levelname)s: %(message)s', 
        level = logging.INFO)
    name = 'ptt'
    redis_key = 'ptt:start_urls'
    board = None
    ## where are restrictions
    year = 2020
    maximum_missing_count = 500
```

## Reference
* scrapy api: https://scrapy.readthedocs.io/en/0.12/index.html
* scrapy-redis api: https://scrapy-redis.readthedocs.io/en/v0.6.1/readme.html
* jianshu personal note: https://www.jianshu.com/p/8a9176d11372
* SCUTJcfeng 's github: https://github.com/SCUTJcfeng/Scrapy-redis-Projects
* ptt website C_Chat board: https://www.ptt.cc/bbs/C_Chat/index.html
* ripples's markdown: http://www.q2zy.com/articles/2015/12/15/note-of-scrapy/
