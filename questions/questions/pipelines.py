# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class DuplicatesPipeline:

    def __init__(self):
        self.questions_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['title'] in self.questions_seen:
            raise DropItem(f'Duplicate item found: {item!r}')
        else:
            self.questions_seen.add(adapter['title'])
            return item

class ContentLengthPipeline:
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('content'):
            if len(adapter.get('content')) > 500:
               return item
        else:
            raise DropItem(f'Too few characters in {item}')
