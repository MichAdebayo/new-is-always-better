# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class JpboxOfficeItem(scrapy.Item):
    film_id = scrapy.Field()
    titre = scrapy.Field()
    genre_principale = scrapy.Field()
    genres = scrapy.Field()
    date_sortie_france = scrapy.Field()
    date_sortie_usa = scrapy.Field()
    duree_minutes = scrapy.Field()
    synopsis = scrapy.Field()
    realisateur = scrapy.Field()
    acteurs = scrapy.Field()
    pays_origine = scrapy.Field()
    budget = scrapy.Field()
    box_office_france = scrapy.Field()
    recette_usa = scrapy.Field()
    recette_monde = scrapy.Field()
    image_url = scrapy.Field()
    note_moyenne = scrapy.Field()
   
    
