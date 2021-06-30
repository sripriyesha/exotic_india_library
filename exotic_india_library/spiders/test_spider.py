import os
import pathlib
import urllib.parse

import scrapy
from scrapy.http import Request


class TestSpider(scrapy.Spider):
    name = "test"
    start_urls = [
        # example book page
        "https://www.exoticindiaart.com/book/details/maitrayani-samhita-its-ritual-and-language-NAB790/?currency=USD"
    ]

    def parse(self, response):
        def get_metadata():
            return {
                "description": response.xpath(
                    "string(normalize-space(//div[@rel='description']))"
                )
                .get(default="")
                .strip(),
            }

        yield get_metadata()
