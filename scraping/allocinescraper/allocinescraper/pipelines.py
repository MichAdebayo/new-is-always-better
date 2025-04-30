# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class AllocineScraperPipeline:
    def process_item(self, item, spider):
        # Iterate over each field in the item and clean string data
        for field, value in item.items():
            if isinstance(value, str):
                item[field] = value.strip()
            elif isinstance(value, list):
                item[field] = [v.strip() for v in value if isinstance(v, str)]
        return item
