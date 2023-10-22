# -*- coding: utf-8 -*-
""""Scrapes product data from online stores"""
import json
import logging
import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.log import configure_logging
from TheSpider.items import Product, Skus, SkuLoader, ProductLoader

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='logging.txt',
    format='%(levelname)s: %(message)s',
    level=logging.DEBUG
)


class APCSpider(scrapy.Spider):
    """Spider class for spider to crawl website"""

    name = "apc_spider"
    start_urls = ["https://www.apc-us.com/"]

    def parse(self, response):
        """Parses initial links"""
        for link in response.css(".chooser a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_categories)

    def parse_categories(self, response):
        """Parses clothing category links"""
        for link in response.css(".go_page::attr(href)").getall():
            yield response.follow(link, callback=self.parse_categories)

        for product_link in response.css(
                ".colorama-product-link-wrapper ::attr(href), .item ::attr(href)").getall():
            yield response.follow(product_link, callback=self.parse_products)

    @staticmethod
    def get_skus(sku, response):
        """Scrapes sku details"""
        sku_loader = SkuLoader(item=Skus(), response=response)
        details = sku["name"].split("/")
        sku_loader.add_value("sku_id", sku["id"])
        sku_loader.add_value("price", sku["price"]/100)
        sku_loader.add_value("colour", details[0].split("-")[-1])
        sku_loader.add_value("size", details[-2].strip())
        sku_loader.add_css("currency", "#in-context-paypal-metadata::attr(data-currency)")
        sku_loader.add_value("out_of_stock", not response.css(
            '[type="application/ld+json"]::text').re_first(
                r'"availability":\s*"(.+)"').endswith("InStock"))
        return sku_loader.load_item()

    def parse_products(self, response):
        """Scrapes required product information"""
        extra_info = json.loads(response.css("script::text").re_first(
            r'\bvar\s+meta\s*=\s*(\{.*?\})\s*;'))
        loader = ProductLoader(item=Product(), response=response)
        loader.add_css("name", ".headline h1::text")
        loader.add_css("category", ".breadcrumbs a::text")
        loader.add_css("image_urls", ".pdp-image-set img::attr(src)")
        loader.add_css(
            "description", ".description::text, .description *::text, .std.ellipsis::text")
        loader.add_css("brand", ".logo span::text")
        loader.add_value("gender", response.css(
            "script::text").re_first(r'"Gender:(\w+)"') or "unisex")
        loader.add_value("retailer_sku", extra_info["product"]["id"])
        for sku in extra_info["product"]["variants"]:
            loader.add_value("skus", self.get_skus(sku, response))
        return loader.load_item()
