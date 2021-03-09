import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess


class HabrNews(scrapy.Item):
    author = scrapy.Field()
    author_karma = scrapy.Field()
    author_rating = scrapy.Field()
    author_specialization = scrapy.Field()
    comments_counter = scrapy.Field()
    hubs = scrapy.Field()
    news_id = scrapy.Field()
    tags = scrapy.Field()
    text = scrapy.Field()
    title = scrapy.Field()


class HabrNewsSpider(scrapy.Spider):
    name = 'habr_news'  # spider_name
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/news/']

    def parse(self, response):
        for news in response.css('article.post_preview'):
            link = news.css('a.post__title_link::attr(href)')[0].root.strip()
            hubs = []
            for hub in response.css('ul.post__hubs inline-list').css('a::text'):
                hubs.append(hub.root.strip())
            yield Request(link, callback=self.parse_item_news,
                          cb_kwargs=dict(hubs=hubs))

        next_page = response.css('a.arrows-pagination__item-link_next::attr(href)')
        if len(next_page) > 0:
            yield Request('https://habr.com' + next_page[0].root.strip(),
                          callback=self.parse)

    def parse_item_news(self, response, hubs):
        author = response.css('span.user-info__nickname::text')[0].root.strip()
        author_karma = response.css('div.stacked-counter__value::text')[0].root.strip()
        author_rating = response.css('div.stacked-counter_rating::text')[0].root.strip()
        author_specialization = response.css('div.user-info__specialization::text')[0].root.strip()
        comments_counter = response.css('span.post-stats__comments-count::text')[0].root.strip()
        news_id = response.css('article.post_full::text')[0].root.strip()
        tags = []
        for tag in response.css('ul.inline-list inline-list_fav-tags js-post-tags').css('a::text'):
            tags.append(tag.root.strip())
        text = response.css('div.post__body_full::text')[0].root.strip()
        title = response.css('span.post__title-text::text')[0].root.strip()

        item = HabrNews()
        item['author'] = author
        item['author_karma'] = author_karma
        item['author_rating'] = author_rating
        item['author_specialization'] = author_specialization
        item['comments_counter'] = int(comments_counter.replace(',', '').replace('\xa0', ''))
        item['hubs'] = hubs
        item['news_id'] = news_id
        item['tags'] = tags
        item['text'] = text
        item['title'] = title

        yield item


if __name__ == '__main__':
    process = CrawlerProcess(settings={
        "FEEDS": {
            # сохранить результаты в файлы
            "./../../habr_news.json": {"format": "json"},
            "./../../habr_news.csv": {"format": "csv"},
        },
        "LOG_LEVEL": "ERROR"        # без логов в терминале
    })

    process.crawl(HabrNewsSpider)

    # the script will block here until the crawling is finished
    process.start()