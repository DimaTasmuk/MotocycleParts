# -*- coding: UTF-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Compose


class MegazipLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = TakeFirst()

    image_link_out = Join(separator='')
    items_catalog_in = MapCompose()
    items_catalog_out = MapCompose()


class MegazipCatalogLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = TakeFirst()

    catalog_item_link_out = Join(separator='')
    catalog_item_number_out = Compose(lambda v: v[-1])
