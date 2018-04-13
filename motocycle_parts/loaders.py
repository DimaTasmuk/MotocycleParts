# -*- coding: UTF-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class MegazipLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = TakeFirst()

    image_link_out = Join(separator='')


class MegazipCatalogLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = TakeFirst()

    catalog_item_price_out = Join(separator='')