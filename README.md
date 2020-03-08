# pttCrawler
In this project we try to collect data from the ptt website. We adopt scrapy framework based on python language and use mongoDB as our storage. However, crawler handles it job only on single machine. To explore efficently, scrapy-redis provides distributed mechanism that helps us running spider on clients. For the purpose of deployment, we use scrapyd to achieve it. 

## Dependencies
- **Python 3** (tested on python 3.7.2)
- **redis 3.4.1** (for cached memory)
- **pymongo 3.10.1** (used nosql db)
- **Scrapy 2.0.0** (framework of crawler)
- **scrapy-redis 0.6.8** (achieve distributed scrawling)
- **scrapyd 1.2.1** (provide a crawling daemon )
- **scrapyd-client 1.1.0** (used to deploy our spider)

## SnapShot
![post info](/assets/img/Screenshot%20from%202020-03-08%2013-23-04.png?raw=true "post item")

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

