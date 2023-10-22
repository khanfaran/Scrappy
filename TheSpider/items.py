# -*- coding: utf-8 -*-
"""Defines Models For Scraped Items"""

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst, Identity
from scrapy.loader import ItemLoader


class Product(scrapy.Item):
    """Product Item Class"""
    name = scrapy.Field()
    category = scrapy.Field()
    image_urls = scrapy.Field()
    description = scrapy.Field()
    brand = scrapy.Field()
    url = scrapy.Field()
    gender = scrapy.Field()
    retailer_sku = scrapy.Field()
    skus = scrapy.Field()


class SkuLoader(ItemLoader):
    """Sku Item Loader"""
    default_output_processor = TakeFirst()


class ProductLoader(ItemLoader):
    default_output_processor = Join()
    name_in = MapCompose(str.strip)
    description_in = MapCompose(str.strip)
    gender_out = TakeFirst()
    retailer_sku_out = TakeFirst()
    category_out = Identity()
    skus_out = Identity()
    image_urls_out = Identity()


class Skus(scrapy.Item):
    """Sku Item Class"""
    sku_id = scrapy.Field()
    price = scrapy.Field()
    colour = scrapy.Field()
    size = scrapy.Field()
    currency = scrapy.Field()
    out_of_stock = scrapy.Field()
    
