import scrapy


class StackoverflowSpider(scrapy.Spider):
    name = 'stackoverflow'
    allowed_domains = ['stackoverflow.com']
    start_urls = ['https://stackoverflow.com/questions?tab=Newest']

    def parse(self, response):
        links = response.css("#questions a.question-hyperlink::attr(href)").extract()
        for link in links:
            yield scrapy.Request(f'https://stackoverflow.com{link}', self.parse_question)

    
    def parse_question(self, response):
        title = response.css('#question-header h1 *::text').get()
        dateCreated = response.css('time[itemprop="dateCreated"]::attr(datetime)').get()
        views = response.css('div[title^="Viewed"]::text').getall()[-1].strip()[0]

        question = response.css('.question')
        votes = question.css('.js-vote-count::text').get()
        tags = question.css('.post-taglist a::text').getall()
        content = question.css('.js-post-body *::text').getall()