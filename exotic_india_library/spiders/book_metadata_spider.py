import os
import pathlib
import urllib.parse

import scrapy
from scrapy.http import Request


class BookMetadataSpider(scrapy.Spider):
    name = "book_metadata"
    start_urls = [
        # example book page
        "https://www.exoticindiaart.com/book/details/maitrayani-samhita-its-ritual-and-language-NAB790/"
    ]

    def parse(self, response):
        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        def get_next_td_anchor_text(key):
            return (
                response.xpath(
                    "//td[contains(text(), '"
                    + key
                    + "')]"
                    + "/following-sibling::td[1]"
                    + "//a//text()"
                )
                .get(default="")
                .strip()
            )

        def get_next_td_text(key):
            return (
                response.xpath(
                    "//td[contains(text(), '"
                    + key
                    + "')]"
                    + "/following-sibling::td[1]"
                    + "//text()"
                )
                .get(default="")
                .strip()
            )

        def get_metadata():
            author = get_next_td_anchor_text("Author:")
            publisher = get_next_td_anchor_text("Publisher:")
            language = get_next_td_text("Language:")
            edition = get_next_td_text("Edition:")
            ISBN = get_next_td_text("ISBN:")
            pages = get_next_td_text("Pages:")
            cover = get_next_td_text("Cover:")
            other_details = get_next_td_text("Other Details:")
            book_weight = (
                response.xpath("//td[contains(text(), 'weight of the book:')]//text()")
                .get(default="")
                .strip()
                .split(":")[1]
                .strip()
            )

            short_description = ""
            if author.strip() != "":
                short_description += "<strong>Author:</strong> " + author + "<br/>"

            if publisher.strip() != "":
                short_description += (
                    "<strong>Publisher:</strong> " + publisher + "<br/>"
                )

            if language.strip() != "":
                short_description += "<strong>Language:</strong> " + language + "<br/>"

            if edition.strip() != "":
                short_description += "<strong>Edition:</strong> " + edition + "<br/>"

            if ISBN.strip() != "":
                short_description += "<strong>ISBN:</strong> " + ISBN + "<br/>"

            if pages.strip() != "":
                short_description += "<strong>Pages:</strong> " + pages + "<br/>"

            if cover.strip() != "":
                short_description += "<strong>Publisher:</strong> " + cover + "<br/>"

            if other_details.strip() != "":
                short_description += (
                    "<strong>Other Details:</strong> " + other_details + "<br/>"
                )

            if book_weight.strip() != "":
                short_description += (
                    "<strong>Book weight:</strong> " + book_weight + "<br/>"
                )

            return {
                "title": extract_with_css("h1.product-details-page-title::text"),
                "images": extract_with_css(
                    "div.product-details-primary-image img::attr(src)"
                ),
                "price": extract_with_css("span.product-details-finalprice::text"),
                "short_description": short_description,
                # Category needs to be changed manually
                "categories": "hindu",
                "description": response.xpath("string(//div[@rel='description'])")
                .get(default="")
                .strip(),
                "meta:author": author,
                "meta:publisher": publisher,
                "meta:language": language,
                "meta:edition": edition,
                "meta:ISBN": ISBN,
                "meta:pages": pages,
                "meta:cover": cover,
                "meta:other_details": other_details,
                "meta:book_weight": book_weight,
            }

        yield get_metadata()
