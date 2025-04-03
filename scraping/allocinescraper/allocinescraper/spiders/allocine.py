import scrapy
from scrapy_splash import SplashRequest
from scrapy.spiders import Spider


class AllocineSpider(scrapy.Spider):
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 1})
    def parse(self, response):
        genre_links = response.css('.filter-entity-desktop a.blue-link::attr(href)').getall()
        for link in genre_links:
            # Only follow genre links, not other links like "Tous les genres"
            if "/films/genre-" in link:
                yield SplashRequest(response.urljoin(link), self.parse_genre, args={'wait': 1})

    def parse_genre(self, response):
        genre_name = response.css('h1.item::text').get().strip()
        movie_titles = response.css('.gd-col-middle h2 a::text').getall()
        yield {
            'genre': genre_name,
            'movies': movie_titles}

# response.css('.filter-entity-word li a::text').getall() - list of genres.
# response.css('.filter-entity-word li a::attr(href)').getall() - href of genres
# response.css('.gd-col-middle li h2 a::text').getall() - titre de films
# response.css('.gd-col-middle li span.date::text').getall() - date de sortie de films
#response.css('.gd-col-middle li div.meta-body-item.meta-body-info::text').getall() - les duration des films
###netoyage  du film text dans pipeline:::[duration.strip() for duration in durations if "min" in duration]
#

