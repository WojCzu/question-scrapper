# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from datetime import datetime as dt


class QuestionsPipeline:
    def __init__(self):
        self.target_date = dt(2021, 6, 1)
        self.questions_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('date_created'):
            date = dt.fromisoformat(adapter.get('date_created'))

            if(date <= self.target_date):
                spider.crawler.engine.close_spider(self, reason='date_reached')

        if adapter.get('content'):
            if len(adapter.get('content')) < 350:
               raise DropItem(f'Too few characters in content of {item}')

        if adapter['title'] in self.questions_seen:
            raise DropItem(f'Duplicate item found: {item!r}')
        else:
            self.questions_seen.add(adapter['title'])
        
        return item