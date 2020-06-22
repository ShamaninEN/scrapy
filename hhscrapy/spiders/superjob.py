# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from hhscrapy.items import HhscrapyItem
import re

class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vakansii/menedzher.html']

    def parse(self, response):
        next_page = response.xpath("//a[contains(@class, 'f-test-link-Dalshe')]/@href").extract_first()
        vacancy_links = response.xpath("//div[contains(@class, 'f-test-vacancy-item')] //a[contains(@href, '/vakansii/')]/@href").extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacansy_parse)

        yield response.follow(next_page, callback=self.parse)


    def vacansy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').extract_first()
        salary = response.xpath('//span[@class="_3mfro _2Wp8I PlM3e _2JVkc"]/text()').extract()
        salary_min = None
        salary_max = None
        if len(salary) > 1:
            ind_0 = re.search(r'\d+\s\d+', salary[0])
            ind_1 = re.search(r'\d+\s\d+', salary[1])
            ind_ot = re.search(r'от', salary[0])
            if ind_0 != None:
                salary_min = int(re.sub(r'\s', '', ind_0[0]))
            elif ind_ot != None:
                s_min = re.search(r'\d+\s\d+', salary[2])
                salary_min = int(re.sub(r'\s', '', s_min[0]))
            if ind_1 != None:
                salary_max = int(re.sub(r'\s', '', ind_1[0]))


        yield HhscrapyItem(name = name, salary_min = salary_min, salary_max = salary_max, link = response.request.url, site = self.allowed_domains[0])
