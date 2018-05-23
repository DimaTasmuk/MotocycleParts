# coding=utf-8
from scrapy import Spider

from motocycle_parts.items import MegazipItem, MegazipCatalogItem
from motocycle_parts.loaders import MegazipLoader, MegazipCatalogLoader


class MegazipParser(Spider):

    name = "megazip"
    ORIGIN_LINK = unicode("https://www.megazip.ru")

    start_urls = ["https://www.megazip.ru/zapchasti-dlya-motocyklov"]
    parsed_details = set()

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
                if part_link not in self.parsed_details:
                    self.parsed_details.add(part_link)
                    yield response.follow(part_link, self.parse_part)

        elif len(response.css("ul.s-catalog__body-variants")) > 0:
            for model in response.css("ul.s-catalog__body-variants li.s-catalog__body-variants-item.tech_row"):
                yield response.follow(model.css("a.s-catalog__body-variants-name::attr(href)").extract_first(), self.parse_model)

    def parse_part(self, response):
        link = unicode(response.url)

        loader = MegazipLoader(item=MegazipItem(), response=response)
        loader.add_value('link', link)
        loader.add_css("title", "div.s-catalog__header p.h1::text")
        loader.add_value("image_link", self.ORIGIN_LINK)
        loader.add_value("image_link", response.css("img.s-catalog__items-image-group::attr(src)").extract_first())
        loader.add_xpath("year", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Год']//following-sibling::dd[1]//text()")
        loader.add_xpath("color", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Цвет']//following-sibling::dd[1]//text()")
        loader.add_xpath("color_variant", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Вариант окраса']//following-sibling::dd[1]//text()")
        loader.add_xpath("model", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Модель']//following-sibling::dd[1]//text()")
        loader.add_xpath("model_code", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Код модели']//following-sibling::dd[1]//text()")
        loader.add_xpath("region", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Регион продаж']//following-sibling::dd[1]//text()")
        loader.add_xpath("engine_capacity", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Объем двигателя']//following-sibling::dd[1]//text()")
        loader.add_xpath("engine", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Двигатель']//following-sibling::dd[1]//text()")
        loader.add_xpath("frame", u"//dl[@class='s-catalog__attrs s-catalog__attrs_type_dotted' or @class='s-catalog__attrs']//dt[text()='Рама']//following-sibling::dd[1]//text()")
        loader.add_value("items_catalog", self.get_items_catalog(response))
        return loader.load_item()

    def get_items_catalog(self, response):
        items_catalog = []
        for item in response.xpath("//table[@class='items-list']/tbody/tr[contains(@class,'items-list__row')]/td[contains(@class, 'items-list__cell_type_description')]/a[@class='items-list__name']"):
            catalog_item = MegazipCatalogLoader(item=MegazipCatalogItem(), selector=item)
            catalog_item.add_xpath('catalog_item_name', "../../td[contains(@class, 'items-list__cell_type_description')]/*[@class='items-list__name']/text()")
            catalog_item.add_value('catalog_item_link', self.ORIGIN_LINK)
            catalog_item.add_value('catalog_item_link', item.xpath("../../td[contains(@class, 'items-list__cell_type_description')]/a[@class='items-list__name']/@href").extract_first())
            catalog_item.add_xpath('catalog_item_number', "../../td[contains(@class, 'items-list__cell_type_number')]/p[@class='items-list__number']/text()")
            catalog_item.add_xpath('catalog_item_price', "../../td[contains(@class, 'items-list__cell_type_price')]/p[@class='items-list__price']/text()", re="[0-9]+(?: )+[0-9]*")

            items_catalog.append(catalog_item.load_item())
        return items_catalog