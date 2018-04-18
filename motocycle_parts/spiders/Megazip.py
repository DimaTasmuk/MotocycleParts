# coding=utf-8
import socks
import socket

from datetime import datetime
from pip._vendor import requests
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider

from motocycle_parts.items import MegazipItem, MegazipCatalogItem
from motocycle_parts.loaders import MegazipLoader, MegazipCatalogLoader


class MegazipParser(Spider):

    name = "megazip"
    ORIGIN_LINK = unicode("https://www.megazip.ru")
    # start_urls = ["https://www.megazip.ru/zapchasti-dlya-motocyklov"]

    def start_requests(self):
        self.configureNetwork()
        urls = ['https://www.megazip.ru/zapchasti-dlya-motocyklov']
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        # yield response.follow(response.css("li.manufacturers__item a::attr(href)").extract()[0], self.filter_by_model)
        for brand_link in response.css("li.manufacturers__item a::attr(href)").extract():
            yield response.follow(brand_link, self.filter_by_model)

    def filter_by_model(self, response):
        # yield response.follow(response.css("ul.s-catalog__columns-list li.filtred_item a::attr(href)").extract()[0], self.parse_model)
        for model_link in response.css("ul.s-catalog__columns-list li.filtred_item a::attr(href)").extract():
            yield response.follow(model_link, self.parse_model)

    def parse_model(self, response):
        if len(response.css("ul.part-group")) > 0:
            for part_link in response.css("li.part-group__item a.part-group__name::attr(href)").extract():
                yield response.follow(part_link, self.parse_part)

        elif len(response.css("ul.s-catalog__body-variants")) > 0:
            for model in response.css("ul.s-catalog__body-variants li.s-catalog__body-variants-item.tech_row"):
                yield response.follow(model.css("a.s-catalog__body-variants-name::attr(href)").extract_first(), self.parse_model)

    def parse_part(self, response):

        loader = MegazipLoader(item=MegazipItem(), response=response)
        loader.add_css("title", "div.s-catalog__header p.h1::text")
        loader.add_value("image_link", self.ORIGIN_LINK)
        loader.add_value("image_link", response.css("img.s-catalog__items-image-group::attr(src)").extract_first())
        loader.add_xpath("year", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted']//dt[text()='Год']//following-sibling::dd[1]//text()")
        loader.add_xpath("color", u"//dl[@class='s-catalog__attrs']//dt[text()='Цвет']//following-sibling::dd[1]//text()")
        loader.add_xpath("model", u"//dl[@class='s-catalog__attrs']//dt[text()='Модель']//following-sibling::dd[1]//text()")
        loader.add_xpath("model_code", u"//dl[@class='s-catalog__attrs']//dt[text()='Код модели']//following-sibling::dd[1]//text()")
        loader.add_xpath("region", u"//dl[@class='s-catalog__attrs']//dt[text()='Регион продаж']//following-sibling::dd[1]//text()")
        loader.add_xpath("engine_capacity", u"//dl[@class='s-catalog__attrs']//dt[text()='Объем двигателя']//following-sibling::dd[1]//text()")
        loader.add_xpath("engine", u"//dl[@class='s-catalog__attrs']//dt[text()='Двигатель']//following-sibling::dd[1]//text()")
        loader.add_xpath("frame", u"//dl[@class='s-catalog__attrs']//dt[text()='Рама']//following-sibling::dd[1]//text()")
        loader.add_value("items_catalog", self.get_items_catalog(response))

        return loader.load_item()

    def get_items_catalog(self, response):
        items_catalog = []
        for item in response.xpath("//table[@class='s-catalog__items-list-table']/tbody[@class='s-catalog__items-list-table-body']/tr/td[@class='spare_name']/a[@class='price-link']"):
            catalog_item = MegazipCatalogLoader(item=MegazipCatalogItem(), selector=item)
            catalog_item.add_css('catalog_item_name', "a::text")
            catalog_item.add_value('catalog_item_link', self.ORIGIN_LINK)
            catalog_item.add_value('catalog_item_link', item.css("a::attr(href)").extract_first())
            catalog_item.add_xpath('catalog_item_number', "../p/text()")
            catalog_item.add_xpath('catalog_item_count', "../../td[@class='qt_in_set']/text()")
            catalog_item.add_xpath('catalog_item_price', "../../td[@class='s-catalog__items-list-prices']/p[@class='s-catalog__items-list-price']/text()")

            items_catalog.append(catalog_item.load_item())
        return items_catalog

    def configureNetwork(self):
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
        socket.socket = socks.socksocket
        self.checkIP()

    def checkIP(self):
        r = requests.get(r'http://jsonip.com')
        ip = r.json()['ip']
        print 'Your IP is', ip, ", time:", datetime.now()

    def check_access(self, code):
        if code == 429:
            raise CloseSpider("cancelled (doesn't access)")
