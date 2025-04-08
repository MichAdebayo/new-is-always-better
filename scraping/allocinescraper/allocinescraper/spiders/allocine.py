import scrapy
from scrapy_splash import SplashRequest
from allocinescraper.items import AllocinescraperItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class AllocineSpider(CrawlSpider):
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'DOWNLOAD_DELAY': 3,
        'AUTOTHROTTLE_ENABLED': True,
        'HTTPCACHE_ENABLED': True,
    }
    
    max_pages = 1
    pages_scraped = 0

    rules = (
        Rule(LinkExtractor(restrict_css='.pagination a'), follow=True, process_request='limit_pages'),
        Rule(LinkExtractor(restrict_css='.meta-title-link'), callback='parse_film'),    

    )

    def limit_pages(self, request, *args):
        if self.pages_scraped >= self.max_pages:
            self.logger.info(f'Stopping after {self.max_pages} pages.')
            return None
        self.pages_scraped += 1
        return request
    
    def parse_film(self, response):
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
        if viewer_rating := response.css('div.rating-mdl.n40.stareval-stars + span.stareval-note::text').get():
            item['viewer_rating'] = float(viewer_rating.replace(',', '.').strip())

        press_critics_count = response.css('span.stareval-review::text').get()
        item['press_critics_count'] = press_critics_count.strip() if press_critics_count else ""
        
        viewer_critics_count = response.css('div.rating-mdl.n35.stareval-stars + span.stareval-note + span.stareval-review.light::text').get()
        item['viewer_critics_count'] = viewer_critics_count.strip() if viewer_critics_count else ""
        # viewer_notes_count = response.css('div.rating-mdl.n40.stareval-stars + span.stareval-note::text').get()
        # item['viewer_notes_count'] = viewer_notes_count.strip() if viewer_notes_count else ""

        item['languages'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Langues")]]//span[contains(@class, "that")]/text()').get(default='').strip()
        item['distributor'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Distributeur")]]//span[contains(@class, "blue-link")]/text()').get(default='').strip()
        item['year_of_production'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Année de production")]]//span[contains(@class, "that")]/text()').get()
        item['film_nationality'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Nationalités")]]//span[contains(@class, "nationality")]/text()').getall()
        item['filming_secrets'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Secrets de tournage")]]//span[contains(@class, "that")]/text()').get()
        item['awards'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Récompenses")]]//span[contains(@class, "that")]/text()').get()
        item['budget'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Budget")]]//span[contains(@class, "that")]/text()').get()
        #actor_data = meta.css('.meta-body-item a::attr(href)').getall()
        # actor_data = meta.xpath('.//div[@class="meta-body-direction"][.//span[contains(text(), "De")]]')
        #item['director_link'] = actor_data.xpath('./a/@href').get()
        #self.logger.info(f"All links: {item['director_link']}")

        # Build the box office URL if it's different
        film_box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/') + 'box-office/'

        yield scrapy.Request(
            film_box_office_url,
            callback=self.parse_box_office_page,
            meta={'item': item},
            dont_filter=True  # Only use this if you're sure it doesn't cause duplicates
        )

    def parse_box_office_page(self, response):
        item = response.meta['item']
 
        # Locate sections by header text rather than by index
        france_section = response.xpath('//section[contains(.//h2/text(), "Box Office France")]')
        us_section = response.xpath('//section[contains(.//h2/text(), "Box Office US")]')

        if france_row := france_section.xpath(
            './/table[contains(@class, "box-office-table")]/tbody/tr[1]'
        ):
            self.extract_entry_and_entry_week(
                france_row, item, 'fr_entry_week', 'fr_entries'
            )
        else:
            item['fr_entry_week'] = item['fr_entries'] = ''

        if us_row := us_section.xpath(
            './/table[contains(@class, "box-office-table")]/tbody/tr[1]'
        ):
            self.extract_entry_and_entry_week(
                us_row, item, 'us_entry_week', 'us_entries'
            )
        else:
            item['us_entry_week'] = item['us_entries'] = ''

        yield item

    def extract_entry_and_entry_week(self, arg0, item, arg2, arg3):
        fr_week_element = arg0.css('td.responsive-table-column.first-col span::text')
        item[arg2] = fr_week_element.get().strip() if fr_week_element else None
        item[arg3] = (
            arg0.xpath('.//td[@data-heading="Entrées"]/text()')
            .get(default='')
            .strip()
        )