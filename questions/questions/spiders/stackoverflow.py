import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags


class QustionItem(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    tags = scrapy.Field()
    votes  = scrapy.Field(input_processor=MapCompose(str.strip), output_processor=TakeFirst())
    views  = scrapy.Field(input_processor=MapCompose(str.strip, lambda x: x.split()), output_processor=TakeFirst())
    date_created  = scrapy.Field(output_processor=TakeFirst())
    content  = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=Join())


class QustionItemLoader(ItemLoader):
    item = QustionItem()
    # default_output_processor = TakeFirst()

class StackoverflowSpider(scrapy.Spider):
    name = 'stackoverflow'
    allowed_domains = ['stackoverflow.com']
    start_urls = ['https://stackoverflow.com/questions?tab=Newest']

    def parse(self, response):
        links = response.css('#questions a.question-hyperlink::attr(href)').extract()
        for link in links:
            yield scrapy.Request(f'https://stackoverflow.com{link}', self.parse_question)
        # yield scrapy.Request(f'https://stackoverflow.com{links[0]}', self.parse_question)
        next_page = response.css('.s-pagination a[rel="next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(f'https://stackoverflow.com{next_page}', self.parse)

    
    def parse_question(self, response):
        question = QustionItemLoader(response=response)
        question.add_css('title', '#question-header h1 *::text')
        question.add_css('date_created', 'time[itemprop="dateCreated"]::attr(datetime)')
        question.add_css('views', 'div[title^="Viewed"]::text')
        question.add_css('tags', '.question .post-taglist a::text')
        question.add_css('votes', '.question .js-vote-count::text')
        question.add_css('content', '.question .js-post-body *::text')
        yield question.load_item()