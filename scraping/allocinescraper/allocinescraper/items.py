# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AllocinescraperItem(scrapy.Item):
    film_title = scrapy.Field()
    film_url = scrapy.Field()
    release_date = scrapy.Field()
    duration = scrapy.Field()
    associated_genres = scrapy.Field()
    producer = scrapy.Field()
    top_stars = scrapy.Field()
    press_review = scrapy.Field()
    viewer_review = scrapy.Field()
    synopsis = scrapy.Field()
    
    
    #associated_genres_urls =  scrapy.Field()


#     # define the fields for your item here like:
#     principal_genre = scrapy.Field()
#     genre_link =  scrapy.Field()
#     # producer_age = scrapy.Field()
#     # 
#     # distributor = scrapy.Field()
#     # country_source = scrapy.Field()
#     # year_of_production = scrapy.Field()
#     # entrances_france = scrapy.Field()
#     # entrances_france_week = scrapy.Field()
#     # cumul_france = scrapy.Field()
#     # entrances_us = scrapy.Field()
#     # entrances_week = scrapy.Field()
#     # cumul_us = scrapy.Field()




