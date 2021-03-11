import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TbbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class TbbSpider(scrapy.Spider):
	name = 'tbb'
	start_urls = ['https://www.tbb.ee/uudised/page/1/']
	page=2
	def parse(self, response):
		articles = response.xpath('//div[@class="fusion-post-content post-content"]')
		for article in articles:
			date = article.xpath('.//p[@class="fusion-single-line-meta"]/span[position()=3]/text()').get()
			post_links = article.xpath('.//h2/a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = f'https://www.tbb.ee/uudised/page/{self.page}/'
		if self.page < 40:
			self.page+=1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="fusion-text fusion-text-1"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TbbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
