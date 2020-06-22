# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from hhscrapy.items import HhscrapyItem
import re
class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=python&fromSearch=true']

    # 1) Доработать паука в имеющемся проекте, чтобы он формировал item по структуре:
    # *Наименование вакансии
    # * Зарплата от
    # * Зарплата до
    # * Ссылку на саму вакансию
    # * Сайт откуда собрана вакансия И складывал все записи в БД(любую)
    # 2) Создать в имеющемся проекте второго паука по сбору вакансий с сайта superjob.Паук должен формировать itemы по аналогичной структуре и складывать данные также в БД

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").extract_first()
        vacansy_links = response.xpath("//div[@class='vacancy-serp']/div[contains(@class, 'vacancy-serp-item')] //a[contains(@class, 'HH-LinkModifier')]/@href").extract()
        for vacansy_link in vacansy_links:
            yield response.follow(vacansy_link, callback=self.vacansy_parse)


        yield response.follow(next_page, callback=self.parse)
    def vacansy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').extract_first()
        salary = response.xpath('//p[@class="vacancy-salary"]/span/text()').extract()
        try:
            s_max = re.search(r'до', salary[0])
        except IndexError:
            salary_max = None
        else:
            if s_max != None:
                try:
                    salary_max = int(re.sub(r'\xa0', '', salary[1]))
                except IndexError:
                    sal_max = re.search(r'\d+\s\d+', salary[0])
                    salary_max = int(re.sub(r'\s', '', sal_max[0]))
            else:
                salary_max = None
        try:
            s_min = re.search(r'от', salary[0])
        except IndexError:
            salary_min = None
        else:
            if s_min != None:
                salary_min = int(re.sub(r'\xa0', '', salary[1]))
            else:
                salary_min = None
        if salary_max == None:
            try:
                s_max = re.search(r'до', salary[2])
            except IndexError:
                salary_max = None
            else:
                if s_max != None:
                    salary_max = int(re.sub(r'\xa0', '', salary[3]))


        yield HhscrapyItem(name = name, salary_min = salary_min, salary_max = salary_max, link = response.request.url, site = self.allowed_domains[0])
