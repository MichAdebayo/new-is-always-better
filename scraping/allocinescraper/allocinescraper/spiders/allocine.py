import shutil
import os
from allocinescraper.items import AllocinescraperItem
from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy

class AllocineSpider(CrawlSpider):
    """
    Spider to crawl and scrape film data from Allociné.

    This spider starts at the Allociné films listing pages and uses Splash to render
    dynamic content for box-office and trailer pages. It extracts film details such as
    title, synopsis, classification, ratings, and more. It also processes the box-office
    data and, if available, the trailer page to extract trailer views.
    """
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr/films/?page=" + str(x) for x in range(1, 20)]

    # CrawlSpider rules:
    # Extract film detail links using an XPath selector and parse each film page.
    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"), callback='parse_film'),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """
        Create the spider instance from crawler settings and connect signals.

        This method attaches a listener to the spider_closed signal to delete the 
        HTTP cache folder after the spider run.
        """
        spider = super(AllocineSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        """
        Called when the spider is closed.
        
        Attempts to remove the HTTP cache folder, logging success or failure.
        """
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
        """
        Parse a film page to extract film details.

        This method extracts film data (title, URL, image, synopsis, classification, etc.)
        from a film detail page. It then constructs the URL for the box-office page and
        initiates a SplashRequest to render and process it.
        """
        self.logger.info(f"Scraping film page: {response.url}")
        item = AllocinescraperItem()
        
        
        # Extract basic film details.
        item['film_title'] = response.css('div.titlebar-title::text').get('').strip()
        item['film_url'] = response.url
        item['film_image_url'] = response.css('img.thumbnail-img::attr(src)').get() or ""
        
        # Extract synopsis and classification.
        synopsis = response.css('div.content-txt p.bo-p::text').get() or response.css('div.content-txt::text').get()
        item['synopsis'] = synopsis.strip() if synopsis else ""
        classification = response.css('div.certificate span.certificate-text::text').get()
        item['age_classification'] = classification.strip() if classification else ""
        
        # Extract additional metadata.
        meta = response.css('div.meta-body')
        item['release_date'] = meta.css('span.date::text').get()
        broadcast_category = response.xpath('//div[contains(@class, "meta-body-info")]//span[contains(@class, "meta-release-type")]/text()').get()
        item['broadcast_category'] = broadcast_category.strip() if broadcast_category else ""
        duration = meta.css('.meta-body-info::text').re_first(r'\d+h\s?\d*min')
        item['duration'] = duration
        
        # Extract genres.
        associated_genres_raw = meta.css('.meta-body-info span.dark-grey-link::text').getall()
        associated_genres_filter = [g.strip() for g in associated_genres_raw if g.strip()]
        item['associated_genres'] = list(dict.fromkeys(associated_genres_filter))
        
        # Extract producers.
        producer_raw = meta.css('.meta-body-direction span::text').getall()
        producer_filter = [p.strip() for p in producer_raw if p.strip().lower() not in ["par", "de"]]
        item['producers'] = list(dict.fromkeys(producer_filter))
        
        # Extract director.
        director = meta.css('.meta-body-direction span.dark-grey-link::text').get()
        item['director'] = director.strip() if director else ""
        
        # Extract actors and top stars.
        actors = meta.css('.meta-body-actor a::text').getall()
        extra_actors = meta.css('.meta-body-actor span.dark-grey-link::text').getall()
        item['top_stars'] = [a.strip() for a in actors + extra_actors if a.strip()]
        
        # Extract press and viewer ratings.
        if press_rating_raw := response.css('span.stareval-note::text').get():
            item['press_rating'] = float(press_rating_raw.replace(',', '.').strip())
        if viewer_rating := response.xpath('//div[contains(@class, "rating-item-content")][.//span[contains(@class, "rating-title") and contains(text(), "Spectateurs")]]//span[contains(@class, "stareval-note")]/text()').get():
            item['viewer_rating'] = float(viewer_rating.replace(',', '.').strip())
        
        # Extract critics counts.
        press_critics_count = response.css('span.stareval-review::text').get()
        item['press_critics_count'] = press_critics_count.strip() if press_critics_count else ""
        viewer_critics_count = response.xpath('//div[contains(@class, "rating-item-content")][.//span[contains(@class, "rating-title") and contains(text(), "Spectateurs")]]//span[contains(@class, "stareval-review")]/text()').get()
        item['viewer_critics_count'] = viewer_critics_count.strip() if viewer_critics_count else ""
        
        # Extract language and distributor information.
        item['languages'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Langues")]]//span[contains(@class, "that")]/text()').get(default='').strip()
        item['distributor'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Distributeur")]]//span[contains(@class, "blue-link")]/text()').get(default='').strip()
        
        # Extract year of production and apply a filter.
        year_of_production_str = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Année de production")]]//span[contains(@class, "that")]/text()').get()
        try:
            year_of_production = int(year_of_production_str) if year_of_production_str else None
            item['year_of_production'] = year_of_production
            if year_of_production and year_of_production < 2000:
                self.logger.info(f"Skipping movie {item.get('film_title')} (year: {year_of_production})")
                return  # Skip movies older than 2000
        except ValueError:
            self.logger.warning(f"Invalid year format: {year_of_production_str}")
            item['year_of_production'] = None
            return  # Skip this movie if the year is invalid
        
        # Extract nationalities, filming secrets, awards and budget.
        item['film_nationality'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Nationalités")]]//span[contains(@class, "nationality")]/text()').getall()
        item['filming_secrets'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Secrets de tournage")]]//span[contains(@class, "that")]/text()').get()
        item['awards'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Récompenses")]]//span[contains(@class, "that")]/text()').get()
        item['budget'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Budget")]]//span[contains(@class, "that")]/text()').get()
        
        # Construct the URL for the film box-office page.
        film_box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/') + 'box-office/'
        
        yield scrapy.Request(
            url=film_box_office_url,
            callback=self.parse_box_office_page,
            meta={'item': item},
            dont_filter=True)

    def parse_box_office_page(self, response):
        """
        Parse the box-office page for a film to extract financial data and then process the trailer.

        This method uses XPath selectors to extract box-office data from France and US sections.
        It then attempts to extract a relative trailer URL to further process the trailer page.
        """
        item = response.meta['item']
        
        # Extract the "Box Office France" section.
        france_section = response.xpath('//section[contains(.//h2/text(), "Box Office France")]')
        # Extract the "Box Office US" section.
        us_section = response.xpath('//section[contains(.//h2/text(), "Box Office US")]')
        
        if france_row := france_section.xpath('.//table[contains(@class, "box-office-table")]/tbody/tr[1]'):
            self.extract_entry_and_entry_week(france_row, item, 'fr_entry_week', 'fr_entries')
        else:
            item['fr_entry_week'] = item['fr_entries'] = ''

        if us_row := us_section.xpath('.//table[contains(@class, "box-office-table")]/tbody/tr[1]'):
            self.extract_entry_and_entry_week(us_row, item, 'us_entry_week', 'us_entries')
        else:
            item['us_entry_week'] = item['us_entries'] = ''

        # Extract the relative trailer URL.
        trailer_relative_url = response.xpath('//div[contains(@class, "roller-slider")]//a[contains(@class, "trailer roller-item")]/@href').get()
        if trailer_relative_url:
            # Build the full trailer URL.
            trailer_url = f'https://www.allocine.fr{trailer_relative_url}'
            yield scrapy.Request(
                url=trailer_url,
                callback=self.parse_trailer_page,
                meta={'item': item},
                dont_filter=True)

        else:
            self.logger.warning(f"No trailer URL found for {item.get('film_title', 'unknown movie')}")
            yield item

    def parse_trailer_page(self, response):
        """
        Parse the trailer page to extract the number of trailer views.

        The method extracts trailer view count from the trailer page, cleans the value,
        and then yields the item.
        """
        item = response.meta['item']
        trailer_views = response.xpath('//div[contains(@class, "media-info-item-holder")]//div[contains(@class, "icon-eye")]/text()').get()
        item['trailer_views'] = trailer_views.strip().replace(' ', ',') if trailer_views else ""
        yield item

    def extract_entry_and_entry_week(self, selector, item, key_week, key_entries):
        """
        Extract the entry week and the entries (ticket count) from a given table row.

        :param selector: The selector for the table row containing the box-office data.
        :param item: The item dictionary to update.
        :param key_week: The key to store the week info.
        :param key_entries: The key to store the entries info.
        """
        fr_week_element = selector.css('td.responsive-table-column.first-col span::text')
        item[key_week] = fr_week_element.get().strip() if fr_week_element else None
        item[key_entries] = selector.xpath('.//td[@data-heading="Entrées"]/text()').get(default='').strip()

    def handle_splash_error(self, failure):
        """
        Handle errors encountered during a SplashRequest.

        Logs the error and yields the current item to avoid data loss.
        """
        self.logger.error(f"Error with Splash: {repr(failure)}")
        yield failure.request.meta['item']