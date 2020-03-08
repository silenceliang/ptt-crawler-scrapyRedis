# pttCrawler

## SnapShot

## Schema design

### Post
| schema | Description |
| --- | --- |
| *canonicalUrl | url where the page visited |
| authorId | who post the article |
| title | title in the article |
| content | content in the article |
| publishedTime | the date this post was created |
| updateTime | the date this post was updated |

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

**Note**: where schema prefix $^*$ represents primary key

## Scrapy-Redis Framework

### Distributed crawling

- master-slaver architecture

1. the master runs spider by following command:
```bash
scrapy crawl pttCrawl
```
2. start redis service and run it :
```bash
redis-cil
```
3. the most important step is to push your url that you attempt to crawl. Here, we use `lpush` to attain this goal. The follwing term `pttCrawl:start_urls` is the redis key we have assigned to our spider.
```bash
lpush pttCrawl:start_urls {ptt url}
```
4. wake our slaver machines up which have a little bit different declaration in `setting.py`:
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

### Deploy to scrapyd
1. scrapyd provide a daemon for crawling. Like http server, we run it by typing the following command:
```bash
scrapyd
```

2. for the purpose of deployment, we install the package `scrapy-client` and run it:
```bash
scrapyd-deploy pttCrawler
```

## Pipeline
* DuplicatesPipeline
> In case of dumplicates in database, we filter the data here.
* MongoPipeline
> save data in database. 
* JsonPipeline
> generate a json file.

