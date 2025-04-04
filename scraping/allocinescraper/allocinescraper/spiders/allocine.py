import scrapy
from scrapy_splash import SplashRequest
from allocinescraper.items import AllocinescraperItem

class AllocineSpider(scrapy.Spider):
    name = "allocine"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'DOWNLOAD_DELAY': 3,  # Add a download delay to be polite
        'AUTOTHROTTLE_ENABLED': True, # Enable autothrottle
        'HTTPCACHE_ENABLED': True # Enable HTTP caching
    }
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/"]
    max_films = None 

    def __init__(self, *args, **kwargs):
        super(AllocineSpider, self).__init__(*args, **kwargs)
        if hasattr(self, 'max_films'):
            try:
                self.max_films = int(self.max_films)
            except (ValueError, TypeError):
                self.max_films = None
    
    def parse_page(self, response):
        films = response.css('.gd-col-middle ul li') 
        scrapped_films = 0

        for film in films:
            if self.max_films and scrapped_films >= self.max_films:
                self.logger.info('Reached the maximum number of films to scrape.')
                break  

            item = AllocinescraperItem()
            if title := film.css('h2 a::text').get():
                item['film_title'] = title.strip()
                item['film_url'] = 'https://www.allocine.fr'+film.css('h2 a::attr(href)').get()
                item['release_date'] = film.css('.date::text').get()
                item['duration'] = film.css('div.meta-body-item.meta-body-info *::text').getall()[4].strip()
                item['associated_genres'] = film.css('.meta-body-info span.dark-grey-link::text').getall()
                item['producer'] = film.css('div.meta-body-item.meta-body-direction span.dark-grey-link::text').getall()
                item['top_stars'] = film.css('.meta-body-actor a.dark-grey-link::text').getall()
                reviews = film.css('.stareval-note::text').getall()
                item['press_review'] = reviews[0].strip() if len(reviews) > 0 and reviews[0].strip() != '--' else None
                item['viewer_review'] = reviews[1].strip() if len(reviews) > 1 and reviews[1].strip() != '--' else None
                
                scrapped_films += 1
                yield SplashRequest(
                    response.urljoin(item['film_url']),
                    self.parse_film,
                    args={'wait': 2},
                    meta={'item': item}
                )
            else:
                self.logger.warning("Film title not found in the response data.")

        if next_page := response.css('.pagination a::attr(href)').get():
            yield response.follow(next_page,
                self.parse_page,)

    def parse_film(self, response):
        principal_item = response.meta.get('item')
        if not principal_item:
            self.logger.error("No item found in response meta.")
            return

        if principal_item['film_url']: 
            self.process_film(principal_item, response)
            yield principal_item

    def process_film(self, principal_item, response):
        block_position = response.css('.gd-col-left')
        principal_item['synopsis'] = block_position.css('div.synopsis p::text').getall()
        principal_item['synopsis'] = [text.strip() for text in principal_item['synopsis'] if text.strip()]

        # principal_item['synopsis'] = ' '.join([text.strip() for text in principal_item['synopsis'] if text.strip()]) if principal_item['synopsis'] else None
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
    #         yield item

        # for film in movie_blocks:
        #     item = AllocinescraperItem(principal_item)
        #     item['film_title'] = film.css('h2 a::text').get()
        #     item['release_date'] = film.css('span.date::text').get()
        #     duration_info = film.css('div.meta-body-item.meta-body-info::text').getall()
        #     item['duration'] = duration_info[2].strip() if len(duration_info) > 2 else None
        #     item['associated_genres'] = film.css('div.meta-body-item.meta-body-info span.dark-grey-link::text').getall()
        #     item['producer'] = film.css('.meta-body-direction span.dark-grey-link::text').getall()
        #     item['top_stars'] = film.css('div.meta-body-item.meta-body-actor span.dark-grey-link::text').getall()
        #     reviews = film.css('div.rating-holder span.stareval-note::text').getall()
        #     item['press_review'] = reviews[0] if reviews else None
        #     item['viewer_review'] = reviews[1] if len(reviews) > 1 else None
        #     self.logger.info(f"Scraped film: {item['film_title']}")
        #     yield item


# class AllocineSpider(scrapy.Spider):
#     name = "allocine"
#     allowed_domains = ["allocine.fr"]
#     start_urls = ["https://www.allocine.fr/films/"]

#     def start_requests(self):
#         # Using SplashRequest for JavaScript-rendered pages
#         for url in self.start_urls:
#             yield SplashRequest(url, self.parse, args={'wait': 2})
    
#     def parse(self, response):
#         """
#         Parse the main films page to extract principal genres and their links.
#         """
#         genres = response.css('.filter-entity-word li a')
#         for genre in genres:
#             item = AllocinescraperItem()
#             item['principal_genre'] = genre.css('::text').get()
#             genre_link = genre.css('::attr(href)').get()
#             if genre_link and "/films/genre-" in genre_link:
#                 item['genre_link'] = response.urljoin(genre_link)
#                 yield SplashRequest(
#                     item['genre_link'],
#                     self.parse_genre,
#                     args={'wait': 2},
#                     meta={'item': item}
#                 )

#     def parse_genre(self, response):
#         genre_name = response.css('h1.item::text').get().strip()
#         movie_titles = response.css('.gd-col-middle h2 a::text').getall()
#         item = {
#             'genre': genre_name,
#             'movies': movie_titles}
#         print("Yielding item:", item)
#         yield item
        
    # def parse_genre(self, response):
    #     """
    #     Parse a genre page to extract films and follow pagination.
    #     """
    #     principal_item = response.meta.get('item')
    #     # Select attributes from film block 
    #     block_position = response.css('.gd-col-middle')
    #     for film in block_position:
    #         item = AllocinescraperItem()
    #         item.update(principal_item)  # inherit principal genre info
    #         item['film_title'] = film.css('li h2 a::text').get()
    #         film_url = film.css('h2 a::attr(href)').get()
    #         item['release_date'] = film.css('li span.date::text').get()
    #         item['duration'] = film.css('li div.meta-body-item.meta-body-info::text').get()[2].strip()
    #         item['associated_genres'] = film.css('div.meta-body-item.meta-body-info span.dark-grey-link::text').getall()
    #         item['producer'] = film.css('li .meta-body-direction span.dark-grey-link::text').getall()
    #         item['top_stars'] = film.css('div.meta-body-item.meta-body-actor span.dark-grey-link::text').getall()
    #         item['press_review'] = film.css('li div.rating-holder.rating-holder span.stareval-note::text').get()[0]
    #         item['viewer_review'] = film.css('li div.rating-holder.rating-holder span.stareval-note::text').get()[1]

            # if film_url:
            #     yield SplashRequest(
            #         response.urljoin(film_url),
            #         self.parse_film,
            #         args={'wait': 2},
            #         meta={'item': item}
            #     )
            # else:
            # yield item

        # if next_page := response.css('a.pagination-next::attr(href)').get():
        #     yield SplashRequest(
        #         response.urljoin(next_page),
        #         self.parse_genre,
        #         args={'wait': 2},
        #         meta={'item': principal_item}
        #     )

    # def parse_film(self, response):
    #     """
    #     Parse the film detail page to extract additional information.
    #     """
    #     item = response.meta.get('item')

    #     item['producer_age'] = response.css('div.producer-age::text').get()
    #     item['synopsis'] = response.css('div.synopsis p::text').get()
    #     item['distributor'] = response.css('div.distributor a::text').get()
    #     item['country_source'] = response.css('div.country-source::text').get()
    #     item['year_of_production'] = response.css('div.production-year::text').get()
    #     item['entrances_france'] = response.css('div.entrances-france::text').get()
    #     item['entrances_france_week'] = response.css('div.entrances-france-week::text').get()
    #     item['cumul_france'] = response.css('div.cumul-france::text').get()
    #     item['entrances_us'] = response.css('div.entrances-us::text').get()
    #     item['entrances_week'] = response.css('div.entrances-week::text').get()
    #     item['cumul_us'] = response.css('div.cumul-us::text').get()

    #     yield item


# response.css('.filter-entity-word li a::text').getall() - list of genres.
# response.css('.filter-entity-word li a::attr(href)').getall() - href of genres




