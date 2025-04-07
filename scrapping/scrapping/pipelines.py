# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JpboxOfficeScraperPipeline:
    def process_item(self, item, spider):
        # Vous pouvez ajouter ici du code pour nettoyer ou transformer les données
        return item