import scrapy
from scrapy_splash import SplashRequest
from allocinescraper.items import AllocinescraperItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re

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

        # Technical details
        #section = response.xpath('//section[contains(@class, "section ovw ovw-technical")]')

        languages = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Langues")]]//span[contains(@class, "that")]/text()').get()
        item['languages'] = languages.strip() if languages else ""

        # distributor= response.xpath('//span[contains(text(), "Distributeur")]/following-sibling::a/text()').get()
        
        # Check the HTML content structure
        section = response.xpath('//section[contains(@class, "section ovw ovw-technical")]')

        distributor = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Distributeur")]]//span[contains(@class, "blue-link")]/text()').get()
        item['distributor'] = distributor.strip() if distributor else ""

        item['year_of_production'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Année de production")]]//span[contains(@class, "that")]/text()').get()

        item['film_nationality'] = response.xpath('//div[contains(@class, "item")][.//span[contains(@class, "what") and contains(text(), "Nationalités")]]//span[contains(@class, "nationality")]/text()').getall()


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



        # principal_item['distributor'] = response.css('div.meta-body-item.meta-body-info a::text').get()
        # principal_item['country_source'] = response.css('div.meta-body-item.meta-body-info span.dark-grey-link::text').get()
        # principal_item['year_of_production'] = response.css('div.meta-body-item.meta-body-info span::text').get()
        # principal_item['entrances_france'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[1]

    
        # principal_item['entrances_france_week'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[2]
        # principal_item['cumul_france'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[3]
        # principal_item['entrances_us'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[4]
        # principal_item['entrances_week'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[5]
        # principal_item['cumul_us'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[6]
        # principal_item['producer_age'] = response.css('div.meta-body-item.meta-body-info span::text').getall()[7]
        # principal_item['associated_genres_urls'] = response.css('div.meta-body-item.meta-body-info a::attr(href)').getall()
        # principal_item['associated_genres_urls'] = [response.urljoin(url) for url in principal_item['associated_genres_urls']]
        # principal_item['associated_genres_urls'] = [url for url in principal_item['associated_genres_urls'] if url and "/films/genre-" in url]
        # principal_item['associated_genres_urls'] = list(set(principal_item['associated_genres_urls']))



    # def parse(self, response):
    #     genres = response.css('.filter-entity-word li a')
    #     if not genres:
    #         self.logger.error("No genres found using selector '.filter-entity-word li a'")
    #     else:
    #         self.logger.info(f"Found {len(genres)} genres")
        
    #     count = 0
    #     for genre in genres:
    #         if self.max_films and count >= int(self.max_films):
    #             self.logger.info('Reached the maximum number of films to scrape.')
    #             return
    #         principal_genre = genre.css('::text').get()
    #         genre_link = genre.css('::attr(href)').get()
    #         if principal_genre and genre_link:
    #             item = AllocinescraperItem()
    #             item['principal_genre'] = principal_genre.strip()
    #             item['genre_link'] = response.urljoin(genre_link.strip())
    #             self.logger.info(f"Extracted genre: {item['principal_genre']} - {item['genre_link']}")
    #             yield SplashRequest(
    #                 item['genre_link'],
    #                 self.parse_genre,
    #                 args={'wait': 2},
    #                 meta={'item': item}
    #             )
    #             count += 1
    #         else:
    #             self.logger.warning("Missing genre name or link in one of the items.")



    #         self.logger.info(f"Scraped film: {item['film_title']}")

    #     item['producer_age'] = response.css('div.producer-age::text').get()
    #     item['distributor'] = response.css('div.distributor a::text').get()
    #     item['country_source'] = response.css('div.country-source::text').get()
    #     item['year_of_production'] = response.css('div.production-year::text').get()
    #     item['entrances_france'] = response.css('div.entrances-france::text').get()
    #     item['entrances_france_week'] = response.css('div.entrances-france-week::text').get()
    #     item['cumul_france'] = response.css('div.cumul-france::text').get()
    #     item['entrances_us'] = response.css('div.entrances-us::text').get()
    #     item['entrances_week'] = response.css('div.entrances-week::text').get()
    #     item['cumul_us'] = response.css('div.cumul-us::text').get()


