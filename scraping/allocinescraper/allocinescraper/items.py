# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AllocinescraperItem(scrapy.Item):
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
    synopsis = scrapy.Field()

    languages = scrapy.Field()
    budget = scrapy.Field()
    distributor =scrapy.Field()
    country_source = scrapy.Field()
    year_of_production = scrapy.Field()
    film_nationality =  scrapy.Field()
    filming_secrets = scrapy.Field()
    color = scrapy.Field()
    fr_entries = scrapy.Field()
    fr_entry_week = scrapy.Field()
    
    
    
    #associated_genres_urls =  scrapy.Field()


#     # define the fields for your item here like:
#     principal_genre = scrapy.Field()
#     genre_link =  scrapy.Field()
#     # producer_age = scrapy.Field()
#     # cumul_france = scrapy.Field()
#     # entrances_us = scrapy.Field()
#     # entrances_week = scrapy.Field()
#     # cumul_us = scrapy.Field()




