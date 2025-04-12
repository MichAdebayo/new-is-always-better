import shutil
from allocinescraper.items import AllocinescraperItem
from scrapy_splash import SplashRequest, SlotPolicy
from scrapy import signals
import os
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class AllocineSpider(CrawlSpider):
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr/films/?page=" + str(x) for x in range(1, 3000)]

    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"), callback='parse_film'),
    )

    max_pages = 1
    pages_scraped = 0

    def limit_pages(self, request, *args):
        if self.pages_scraped >= self.max_pages:
            self.logger.info(f'Stopping after {self.max_pages} pages.')
            return None
        self.pages_scraped += 1
        return request

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AllocineSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Auto-delete cache folder after spider run
        cache_dir = self.settings.get('HTTPCACHE_DIR', 'httpcache')
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                self.logger.info("HTTP cache folder '%s' has been removed.", cache_dir)
            except Exception as e:
                self.logger.error("Failed to remove HTTP cache folder '%s': %s", cache_dir, str(e))
        else:
            self.logger.info("No HTTP cache folder found to remove.")