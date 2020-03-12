FROM python:3.7

MAINTAINER silenceliang <l3754902@gmail.com>

ENV PATH /usr/local/bin:$PATH

COPY . /pttCrawler

WORKDIR /pttCrawler

RUN pip install -r requirements.txt

# allow anyone to connect
COPY default_scrapyd.conf /usr/local/lib/python3.7/site-packages/scrapyd/default_scrapyd.conf

#CMD ["scrapyd"]

ENTRYPOINT ["scrapy", "crawl"]

CMD ["ptt", "-a", "start=3/5", "-a", "end=3/6"]
