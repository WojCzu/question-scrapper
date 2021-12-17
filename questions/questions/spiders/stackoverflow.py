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

    author_name = scrapy.Field(input_processor=MapCompose(str.strip), output_processor=TakeFirst())
    author_questions_number = scrapy.Field(output_processor=TakeFirst())
    author_answers_number = scrapy.Field(output_processor=TakeFirst())
    author_top_tags = scrapy.Field()
    author_account_date_created = scrapy.Field(output_processor=TakeFirst())


class QustionItemLoader(ItemLoader):
    item = QustionItem()


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

        author_link = response.css('#question .user-details[itemprop="author"] a::attr(href)').get()
        yield scrapy.Request(f'https://stackoverflow.com{author_link}', self.parse_author, meta={'question': question})
    
    def parse_author(self, response):
        question = response.meta['question']
        # question.context['response'] = response #loooks good, doesn't work

        question.add_value('author_name', response.css('.fs-headline2::text').get())
        question.add_value('author_questions_number', response.css('#stats .s-card .flex--item:nth-child(3) div::text').get())
        question.add_value('author_answers_number', response.css('#stats .s-card .flex--item:nth-child(4) div::text').get())
        question.add_value('author_top_tags', response.css('#top-tags a.s-tag::text').extract())
        question.add_value('author_account_date_created', response.css('#mainbar-full div.flex--item ul:nth-of-type(1) span::attr(title)').get() )

        yield question.load_item()