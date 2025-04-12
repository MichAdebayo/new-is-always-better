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


    def parse_film(self, response):
        self.logger.info(f"Scraping film page: {response.url}")
        item = AllocinescraperItem()
        item['film_title'] = response.css('div.titlebar-title::text').get('').strip()
        item['film_url'] = response.url
        item['film_image_url'] = response.css('img.thumbnail-img::attr(src)').get() or ""     

        synopsis = response.css('div.content-txt p.bo-p::text').get() or response.css('div.content-txt::text').get()
        item['synopsis'] = synopsis.strip() if synopsis else ""
        classification = response.css('div.certificate span.certificate-text::text').get()
        item['age_classification'] = classification.strip() if classification else ""

        meta = response.css('div.meta-body')
        item['release_date'] = meta.css('span.date::text').get()

        broadcast_category = response.xpath('//div[contains(@class, "meta-body-info")]//span[contains(@class, "meta-release-type")]/text()').get()
        item['broadcast_category'] = broadcast_category.strip() if broadcast_category else ""

        duration = meta.css('.meta-body-info::text').re_first(r'\d+h\s?\d*min')
        item['duration'] = duration

        associated_genres_raw = meta.css('.meta-body-info span.dark-grey-link::text').getall()
        associated_genres_filter = [g.strip() for g in associated_genres_raw if g.strip()]
        item['associated_genres'] = list(dict.fromkeys(associated_genres_filter))

        producer_raw = meta.css('.meta-body-direction span::text').getall()
        producer_filter = [p.strip() for p in producer_raw if p.strip().lower() not in ["par", "de"]]
        item['producers'] = list(dict.fromkeys(producer_filter))

        director = meta.css('.meta-body-direction span.dark-grey-link::text').get()
        item['director'] = director.strip() if director else ""

        actors = meta.css('.meta-body-actor a::text').getall()
        extra_actors = meta.css('.meta-body-actor span.dark-grey-link::text').getall()
        item['top_stars'] = [a.strip() for a in actors + extra_actors if a.strip()]

        if press_rating_raw := response.css('span.stareval-note::text').get():
            item['press_rating'] = float(press_rating_raw.replace(',', '.').strip())
        if viewer_rating := response.xpath('//div[contains(@class, "rating-item-content")][.//span[contains(@class, "rating-title") and contains(text(), "Spectateurs")]]//span[contains(@class, "stareval-note")]/text()').get():
            item['viewer_rating'] = float(viewer_rating.replace(',', '.').strip())

        press_critics_count = response.css('span.stareval-review::text').get()
        item['press_critics_count'] = press_critics_count.strip() if press_critics_count else ""
        
        viewer_critics_count =  response.xpath('//div[contains(@class, "rating-item-content")][.//span[contains(@class, "rating-title") and contains(text(), "Spectateurs")]]//span[contains(@class, "stareval-review")]/text()').get()
        item['viewer_critics_count'] = viewer_critics_count.strip() if viewer_critics_count else ""

        item['languages'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Langues")]]//span[contains(@class, "that")]/text()').get(default='').strip()
        item['distributor'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Distributeur")]]//span[contains(@class, "blue-link")]/text()').get(default='').strip()

        year_of_production_str = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Année de production")]]//span[contains(@class, "that")]/text()').get()
        try:
            year_of_production = int(year_of_production_str) if year_of_production_str else None
            item['year_of_production'] = year_of_production
            if year_of_production and year_of_production < 2000:
                self.logger.info(f"Skipping movie {item.get('film_title')} (year: {year_of_production})")
                return
        except ValueError:
            self.logger.warning(f"Invalid year format: {year_of_production_str}")
            item['year_of_production'] = None
            return
        
        item['film_nationality'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Nationalités")]]//span[contains(@class, "nationality")]/text()').getall()
        item['filming_secrets'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Secrets de tournage")]]//span[contains(@class, "that")]/text()').get()
        item['awards'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Récompenses")]]//span[contains(@class, "that")]/text()').get()
        item['budget'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Budget")]]//span[contains(@class, "that")]/text()').get()
        
        # Process box-office and trailer next via Splash
        film_box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/') + 'box-office/'
        
        yield SplashRequest(
            url=film_box_office_url,
            callback=self.parse_box_office_page,
            meta={'item': item},
            endpoint='render.html',
            slot_policy=SlotPolicy.PER_DOMAIN,
            dont_filter=True
        )

    def parse_box_office_page(self, response):
        item = response.meta['item']
        france_section = response.xpath('//section[contains(.//h2/text(), "Box Office France")]')
        us_section = response.xpath('//section[contains(.//h2/text(), "Box Office US")]')

        if france_row := france_section.xpath('.//table[contains(@class, "box-office-table")]/tbody/tr[1]'):
            self.extract_entry_and_entry_week(france_row, item, 'fr_entry_week', 'fr_entries')
        else:
            item['fr_entry_week'] = item['fr_entries'] = ''

        if us_row := us_section.xpath('.//table[contains(@class, "box-office-table")]/tbody/tr[1]'):
            self.extract_entry_and_entry_week(us_row, item, 'us_entry_week', 'us_entries')
        else:
            item['us_entry_week'] = item['us_entries'] = ''

        trailer_relative_url = response.xpath('//div[contains(@class, "roller-slider")]//a[contains(@class, "trailer roller-item")]/@href').get()
        if trailer_relative_url:
            trailer_url = f'https://www.allocine.fr{trailer_relative_url}'
            yield SplashRequest(
                url=trailer_url,
                callback=self.parse_trailer_page,
                errback=self.handle_splash_error,
                meta={'item': item},
                endpoint='render.html',
                slot_policy=SlotPolicy.PER_DOMAIN,
                dont_filter=True
            )
        else:
            self.logger.warning(f"No trailer URL found for {item.get('film_title', 'unknown movie')}")
            yield item

    def parse_trailer_page(self, response):
        item = response.meta['item']
        trailer_views = response.xpath('//div[contains(@class, "media-info-item-holder")]//div[contains(@class, "icon-eye")]/text()').get()
        item['trailer_views'] = trailer_views.strip().replace(' ', ',') if trailer_views else ""
        yield item

    def extract_entry_and_entry_week(self, selector, item, key_week, key_entries):
        fr_week_element = selector.css('td.responsive-table-column.first-col span::text')
        item[key_week] = fr_week_element.get().strip() if fr_week_element else None
        item[key_entries] = selector.xpath('.//td[@data-heading="Entrées"]/text()').get(default='').strip()

    def handle_splash_error(self, failure):
        self.logger.error(f"Error with Splash: {repr(failure)}")
        yield failure.request.meta['item']