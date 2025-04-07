import scrapy
from scrapy_splash import SplashRequest
from allocinescraper.items import AllocinescraperItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from lxml import html

class AllocineSpider(CrawlSpider):
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'DOWNLOAD_DELAY': 3,  # Add delay to be polite
        'AUTOTHROTTLE_ENABLED': True,
        'HTTPCACHE_ENABLED': True
    }
    
    max_pages = 1  # Limit number of pages to scrape
    pages_scraped = 0  # Counter to track scraped pages

    rules = (
        Rule(LinkExtractor(restrict_css='.pagination a'), follow=True, process_request='limit_pages'),
        Rule(LinkExtractor(restrict_css='.meta-title-link'), callback='parse_film'),
    )

    def limit_pages(self, request, *args):
        """ Stop following pagination links after max_pages """
        if self.pages_scraped >= self.max_pages:
            self.logger.info(f'Stopping after {self.max_pages} pages.')
            return None  # Stop following more pages
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

        # Meta block
        meta = response.css('div.meta-body')

        item['release_date'] = meta.css('span.date::text').get()

        duration = meta.css('.meta-body-info::text').re_first(r'\d+h\s?\d*min')
        item['duration'] = duration

        producer_raw = meta.css('.meta-body-direction span::text').getall()
        producer_filter = [p.strip() for p in producer_raw if p.strip().lower() not in ["par", "de"]]
        item['producers'] = list(dict.fromkeys(producer_filter))

        item['director'] = meta.css('.meta-body-direction span.dark-grey-link::text').get().strip()

        actors = meta.css('.meta-body-actor a::text').getall()
        extra_actors = meta.css('.meta-body-actor span.dark-grey-link::text').getall()
        item['top_stars'] = [a.strip() for a in actors + extra_actors if a.strip()]

        if press_rating_raw := response.css(
            'span.stareval-note::text'
        ).get():
            item['press_rating'] = float(press_rating_raw.replace(',', '.').strip())

        if viewer_rating := response.css(
            'div.rating-mdl.n40.stareval-stars + span.stareval-note::text'
            ).get():
            viewer_rating = float(viewer_rating.replace(',', '.').strip())
            item['viewer_rating'] = viewer_rating

        # Film Technical details
        section = response.xpath('//section[contains(@class, "section ovw ovw-technical")]')

        languages = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Langues")]]//span[contains(@class, "that")]/text()').get()
        item['languages'] = languages.strip() if languages else ""

        distributor = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Distributeur")]]//span[contains(@class, "blue-link")]/text()').get()
        item['distributor'] = distributor.strip() if distributor else ""

        item['year_of_production'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Année de production")]]//span[contains(@class, "that")]/text()').get()

        item['film_nationality'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Nationalités")]]//span[contains(@class, "nationality")]/text()').getall()

        item['filming_secrets'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Secrets de tournage")]]//span[contains(@class, "that")]/text()').get()

        item['color'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Couleur")]]//span[contains(@class, "that")]/text()').get()


        # Film Box Office details
        item['fr_entry_week'] = response.css("td.responsive-table-column.second-col.col-bg::text").get().strip()
        # item['fr_entry_week'] = response.xpath('//h2[contains(@class, "titlebar-title") and contains(text(), "Box Office France")]/following-sibling::table[1]//tbody/tr/td[@data-heading="Semaine"]/text()').get()
        # item['fr_entries'] = response.xpath('//div[contains(@class, "gd-col-left")]//section[contains(@class, "section")]//table[contains(@class, "box-office-table")]//tr[contains(@class, "responsive-table-row")]/td[2]/text()').get()
        # item['fr_cumul'] = response.xpath('//div[contains(@class, "gd-col-left")]//section[contains(@class, "section")]//table[contains(@class, "box-office-table")]//tr[contains(@class, "responsive-table-row")]/td[3]/text()').get()





        #item['fr_entries'] = france_section.xpath('./td[2]//text()').get(default='').strip()
        #item['fr_entry_week'] = france_section.xpath('./td[1]//text()').get(default='').strip()
        # fr_cumul = france_data.xpath('.//td[3]/text()').get().strip()

# # Page Box Office
#         box_office_link = response.xpath('//a[contains(text(), "Box Office") or contains(@title, "Box Office")]/@href').get()
        
#         if box_office_link:
#         # Suivre le lien vers la page de box office
#             box_office_url = response.urljoin(box_office_link)
#             self.log(f"Suivre le lien box office: {box_office_url}")
        
#         # Passer l'objet item actuel à la fonction de callback pour continuer à le remplir
#             yield scrapy.Request(
#                 box_office_url, 
#                 self.parse_box_office_page, 
#                 meta={'item': item}
#             )
#         else:
#         # Si pas de lien box office, retourner l'item tel quel
#             self.log(f"Pas de lien box office trouvé pour {item['titre']}")
            
        # budget = response.xpath('//div[contains(text(), "Budget")]/following-sibling::div/text()').get()
        # item['budget'] = budget.strip() if budget else ""

        # genres = meta.css('.meta-body-info span.dark-grey-link::text').getall()
        # item['associated_genres'] = [g.strip() for g in genres if g.strip()]

        # if press_critics_text := response.css(
        #     'span.stareval-review.light::text'
        # ).get():
        #     item['press_critics_count'] = int(press_critics_text.strip().split()[0])

        # # Select the viewer rating block (div that has n40)
        # viewer_block = response.xpath('//div[contains(@class, "rating-item")][.//div[contains(@class, "rating-mdl") and contains(@class, "n40")]]')
        # print(viewer_block.get())

        # if viewer_reviews_text := viewer_block.xpath(
        #     './/span[contains(@class, "stareval-review light")]/text()'
        # ).get():
        #     viewer_reviews_text = viewer_reviews_text.replace('\xa0', ' ').strip()

        #     # Debugging: Check cleaned review text
        #     print(f"Cleaned Review Text: {viewer_reviews_text}")

        #     # Use a more flexible regex pattern to match 'notes' and 'critiques' numbers
        #     matches = re.findall(r'(\d{1,5})\s+notes,\s+(\d{1,5})\s+critiques', viewer_reviews_text)

        #     # Debugging: Check what the matches look like
        #     print(f"Extracted Matches: {matches}")

        #     # Initialize variables for notes and critiques counts
        #     viewer_notes_count = 0
        #     viewer_critics_count = 0

        #     # Assign values based on the extracted matches
        #     for match in matches:
        #         notes, critiques = match
        #         viewer_notes_count = int(notes)
        #         viewer_critics_count = int(critiques)

        #         # Assign values to the item
        #         item['viewer_notes_count'] = viewer_notes_count
        #         item['viewer_critics_count'] = viewer_critics_count

        # else:
        #     item['viewer_notes_count'] = 0
        #     item['viewer_critics_count'] = 0


        yield item

    # self.logger.warning("Missing genre name or link in one of the items."
    # self.logger.info(f"Scraped film: {item['film_title']}")



