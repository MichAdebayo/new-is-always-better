# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AllocinescraperItem(scrapy.Item):
    # Basic Film Details
    # These fields are used to store basic information about the film.
    film_title = scrapy.Field()
    film_url = scrapy.Field()
    film_image_url = scrapy.Field()
    release_date = scrapy.Field()
    duration = scrapy.Field()
    age_classification = scrapy.Field()
    associated_genres = scrapy.Field()
    producers = scrapy.Field()
    director = scrapy.Field()
    top_stars = scrapy.Field()
    press_rating = scrapy.Field()
    press_critics_count = scrapy.Field()
    viewer_rating = scrapy.Field()
    viewer_notes_count = scrapy.Field()
    viewer_critics_count = scrapy.Field()
    director_link = scrapy.Field()
    synopsis = scrapy.Field()

    # Technical Details
    languages = scrapy.Field()
    budget = scrapy.Field()
    distributor =scrapy.Field()
    country_source = scrapy.Field()
    year_of_production = scrapy.Field()
    film_nationality =  scrapy.Field()
    filming_secrets = scrapy.Field()
    awards = scrapy.Field()
    budget = scrapy.Field()

    # Box Office Details
    fr_entries = scrapy.Field()
    us_entries = scrapy.Field()
    fr_entry_week = scrapy.Field()
    us_entry_week = scrapy.Field()





