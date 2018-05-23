# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class MegazipItem(scrapy.Item):
    link = Field()
    title = Field()
    model = Field()
    model_code = Field()
    image_link = Field()
    year = Field()
    region = Field()
    engine_capacity = Field()
    engine = Field()
    color = Field()
    color_variant = Field()
    frame = Field()
    items_catalog = Field()


class MegazipCatalogItem(scrapy.Item):
    catalog_item_name = Field()
    catalog_item_link = Field()
    catalog_item_number = Field()
    catalog_item_price = Field()
